from sys import platform
from threading import Thread
from queue import Queue, Empty
from typing import Callable
from terminal.tui.Drawable import Drawable

IS_WINDOWS = platform == "win32"

if IS_WINDOWS:
    import msvcrt
    import time
else:
    from os import read as os_read
    from sys import stdin
    from select import select
    from tty import setcbreak
    from termios import tcsetattr, tcgetattr, TCSADRAIN, IXON, IEXTEN, ISIG
    from codecs import getincrementaldecoder

CSI_KEYS = {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left',
            'H': 'home', 'F': 'end', 'Z': 'shift+tab'}
TILDE_KEYS = {1: 'home', 2: 'insert', 3: 'delete', 4: 'end', 5: 'pageup',
              6: 'pagedown', 7: 'home', 8: 'end',
              11: 'f1', 12: 'f2', 13: 'f3', 14: 'f4', 15: 'f5',
              17: 'f6', 18: 'f7', 19: 'f8', 20: 'f9', 21: 'f10',
              23: 'f11', 24: 'f12'}
SS3_KEYS = {'P': 'f1', 'Q': 'f2', 'R': 'f3', 'S': 'f4',
            'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left',
            'H': 'home', 'F': 'end'}

WIN_SCANCODES = {
    72: 'up', 80: 'down', 77: 'right', 75: 'left',
    71: 'home', 79: 'end', 82: 'insert', 83: 'delete',
    73: 'pageup', 81: 'pagedown', 15: 'shift+tab',
    59: 'f1', 60: 'f2', 61: 'f3', 62: 'f4', 63: 'f5',
    64: 'f6', 65: 'f7', 66: 'f8', 67: 'f9', 68: 'f10',
    133: 'f11', 134: 'f12'
}

class InputHandler:
    def __init__(self, capture_signals: bool=False):
        self.running = False
        self.event_queue = Queue()
        self.frame_events = []
        self.owner = None
        self._frame_owner = None
        self.thread = None

        if not IS_WINDOWS:
            self.fd = stdin.fileno()
            self.old_settings = tcgetattr(self.fd)
            setcbreak(self.fd)

            attrs = tcgetattr(self.fd)
            attrs[0] &= ~IXON
            attrs[3] &= ~IEXTEN
            if capture_signals:
                attrs[3] &= ~ISIG
            tcsetattr(self.fd, TCSADRAIN, attrs)

            self._buf = b""
            self._decoder = getincrementaldecoder("utf-8")(errors="ignore")

    def start(self) -> None:
        self.running = True
        target_fn = self._listen_windows if IS_WINDOWS else self._listen_unix
        self.thread = Thread(target=target_fn, daemon=True)
        self.thread.start()

    def _listen_unix(self) -> None:
        while self.running:
            timeout = 0.03 if self._buf else 0.05
            if select([self.fd], [], [], timeout)[0]:
                data = os_read(self.fd, 256)
                if not data:
                    continue
                self._buf += data
                final = False
            else:
                final = True
            for ev in self._parse(final):
                self.event_queue.put(ev)

    def _listen_windows(self) -> None:
        while self.running:
            if msvcrt.kbhit():
                b = msvcrt.getch()
                if b in (b'\x00', b'\xe0'):
                    scancode = ord(msvcrt.getch())
                    ev = WIN_SCANCODES.get(scancode, f"win-{scancode}")
                    self.event_queue.put(ev)
                else:
                    char_code = ord(b)
                    if char_code == 0x1b:
                        self.event_queue.put('esc')
                    elif char_code in (0x09, 0x0a, 0x0d, 0x08):
                        self.event_queue.put(chr(char_code))
                    elif char_code == 0x7f:
                        self.event_queue.put('\x08')
                    elif char_code == 0x00:
                        self.event_queue.put('ctrl+space')
                    elif char_code < 0x20:
                        self.event_queue.put('ctrl+' + chr(char_code + 96))
                    else:
                        try:
                            self.event_queue.put(b.decode('utf-8'))
                        except Exception:
                            pass
            else:
                time.sleep(0.01)

    def _parse(self, final: bool) -> list[str]:
        out, buf, i, n = [], self._buf, 0, len(self._buf)
        while i < n:
            b = buf[i]
            if b == 0x1b:
                if i + 1 >= n:
                    if final: out.append('esc'); i += 1; continue
                    break
                nxt = buf[i + 1]
                if nxt in (0x5b, 0x4f):
                    j = i + 2
                    if nxt == 0x5b:
                        while j < n and not (0x40 <= buf[j] <= 0x7e): j += 1
                    if j >= n:
                        if final: out.append('esc'); i += 1; continue
                        break
                    body = buf[i + 2:j].decode('ascii', 'ignore')
                    fin = chr(buf[j])
                    out.append(self._name(nxt == 0x4f, body, fin))
                    i = j + 1
                    continue
                if nxt == 0x1b: out.append('esc'); i += 1; continue
                if nxt < 0x80: out.append('alt+' + chr(nxt)); i += 2; continue
                out.append('esc'); i += 1; continue
            if b in (0x09, 0x0a, 0x0d, 0x08, 0x7f): out.append(chr(b))
            elif b == 0x00: out.append('ctrl+space')
            elif b < 0x20: out.append('ctrl+' + (chr(b + 96) if b <= 26 else chr(b + 64)))
            else:
                ch = self._decoder.decode(buf[i:i + 1])
                if ch: out.append(ch)
            i += 1
        self._buf = buf[i:]
        return out

    @staticmethod
    def _name(ss3: bool, body: str, fin: str) -> str:
        if ss3: return SS3_KEYS.get(fin, f'ss3-{fin}')
        parts = body.split(';')
        mods = ''
        if len(parts) > 1 and parts[1].isdigit():
            m = int(parts[1]) - 1
            mods = ('shift+' if m & 1 else '') + ('alt+' if m & 2 else '') + ('ctrl+' if m & 4 else '')
        if fin == '~' and parts[0].isdigit():
            return mods + TILDE_KEYS.get(int(parts[0]), f'csi-{body}~')
        return mods + CSI_KEYS.get(fin, f'csi-{body}{fin}')

    def capture(self, owner: Drawable) -> bool:
        if self.owner is None or self.owner is owner:
            self.owner = owner
            return True
        return False

    def release(self, owner: Drawable, force=False) -> None:
        if self.owner is owner or force:
            self.owner = None

    def flush_events(self) -> None:
        self.frame_events = []
        while True:
            try:
                self.frame_events.append(self.event_queue.get_nowait())
            except Empty:
                break
        self._frame_owner = self.owner

    def poll_events(self, fn: Callable[[str], None], owner=None, always=False) -> None:
        if not always:
            if owner is None and self._frame_owner is not None: return
            if owner is not None and self._frame_owner is not owner: return
        for e in self.frame_events:
            fn(e)

    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.2)
        if not IS_WINDOWS:
            tcsetattr(self.fd, TCSADRAIN, self.old_settings)
