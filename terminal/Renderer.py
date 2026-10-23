import sys, os, shutil, time

IS_WINDOWS = sys.platform == "win32"
if not IS_WINDOWS:
    import select

Clip = tuple[int, int, int, int]


class Renderer:
    def __init__(self, bg_char: str = " "):
        self.bg_char = bg_char
        self.width = self.height = 0
        self.buffer: list[list[str]] = []
        self.vertical_scale = 1.0
        self.started = False
        self._size: tuple[int, int] | None = None

    def start(self) -> None:
        if self.started:
            return
        sys.stdout.write("\033[?1049h\033[?25l")
        sys.stdout.flush()
        self.started = True
        self.vertical_scale = self._measure_vertical_scale()
        self.begin_frame()

    def close(self) -> None:
        if not self.started:
            return
        sys.stdout.write("\033[?1049l\033[?25h")
        sys.stdout.flush()
        self.started = False

    def _measure_vertical_scale(self) -> float:
        if IS_WINDOWS:
            return 1.0
        sys.stdout.write("\033[9999;9999H\033[6n")
        sys.stdout.flush()
        fd = sys.stdin.fileno()
        response = b""
        deadline = time.time() + 0.3
        while time.time() < deadline:
            if select.select([fd], [], [], 0.05)[0]:
                response += os.read(fd, 32)
                if response.endswith(b"R"):
                    break
        try:
            coords = response.decode().split("\x1b[")[1].split("R")[0]
            visible_lines, _ = map(int, coords.split(";"))
            _, reported = shutil.get_terminal_size()
            if reported > 0:
                return visible_lines / reported
        except Exception:
            pass
        return 1.0

    def begin_frame(self) -> None:
        cols, lines = shutil.get_terminal_size(fallback=(80, 24))
        if (cols, lines) != self._size:
            self._size = (cols, lines)
            self.width = cols
            self.height = max(1, int(lines * self.vertical_scale) - 1)
            self.buffer = [[self.bg_char] * self.width for _ in range(self.height)]
            if self.started:
                sys.stdout.write("\033[2J")
            return
        blank = [self.bg_char] * self.width
        for row in self.buffer:
            row[:] = blank

    def render(self) -> None:
        sys.stdout.write("\033[H" + "\n".join("".join(r) for r in self.buffer))
        sys.stdout.flush()

    def draw(self, x: int, y: int, text: str, clip: Clip | None= None) -> None:
        x0, y0, x1, y1 = 0, 0, self.width, self.height
        if clip is not None:
            cx, cy, cw, ch = clip
            x0, y0 = max(x0, cx), max(y0, cy)
            x1, y1 = min(x1, cx + cw), min(y1, cy + ch)
        if not y0 <= y < y1:
            return
        start, end = max(x, x0), min(x + len(text), x1)
        if start < end:
            self.buffer[y][start:end] = text[start - x:end - x]

    def draw_cursor(self, x: int, y: int, ch: str = " ", clip: Clip | None = None) -> None:
        x0, y0, x1, y1 = 0, 0, self.width, self.height
        if clip is not None:
            cx, cy, cw, chh = clip
            x0, y0 = max(x0, cx), max(y0, cy)
            x1, y1 = min(x1, cx + cw), min(y1, cy + chh)
        if x0 <= x < x1 and y0 <= y < y1:
            self.buffer[y][x] = f"\033[7m{ch or ' '}\033[0m"