import sys, os, shutil, time, select

class Renderer:
    def __init__(self, bg_char: str=" "):
        self.bg_char = bg_char
        self.width = self.height = 0
        self.buffer = []
        sys.stdout.write("\033[?1049h\033[?25l")
        sys.stdout.flush()
        self.vertical_scale = self._initialize_aspect_ratio()
        self.update_dimensions()

    def _initialize_aspect_ratio(self) -> float:
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

    def update_dimensions(self) -> None:
        cols, lines = shutil.get_terminal_size(fallback=(80, 24))
        self.width = cols
        self.height = max(1, int(lines * self.vertical_scale) - 1)
        self.clear()

    def clear(self) -> None:
        self.buffer = [[self.bg_char] * self.width for _ in range(self.height)]

    def draw(self, x: int, y: int, text: str) -> None:
        if not 0 <= y < self.height:
            return
        for i, ch in enumerate(text):
            if 0 <= x + i < self.width:
                self.buffer[y][x + i] = ch

    def render(self) -> None:
        sys.stdout.write("\033[H" + "\n".join("".join(r) for r in self.buffer))
        sys.stdout.flush()

    def close(self) -> None:
        sys.stdout.write("\033[?1049l\033[?25h")
        sys.stdout.flush()
