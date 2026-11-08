from typing import Callable
from time import monotonic
from terminal.tui.Drawable import Drawable

MASK_CHAR = "*"

class TextInput(Drawable):
    focusable = True
    def __init__(
        self,
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        onSubmit: Callable[[str], None] | None = None,
        prompt: str = "> ",
        width: int = 20,
        max_chars: int = 256,
        blink_rate: float = 0.5,
        clear_text_on_submit: bool = True,
        hidden: bool = False,
        autofocus: bool = False,
        style: tuple[int, ...] = ()
    ):
        super().__init__(position, anchor_point, size)
        self.prompt = prompt
        self.width = width
        self.max_chars = max_chars
        self.blink_rate = blink_rate
        self.onSubmit = onSubmit
        self.clear_text_on_submit = clear_text_on_submit
        self.hidden = hidden

        self.text_buffer = ""
        self.cursor = 0
        self.submitted_text = ""
        self.style = style
        self.focused = False
        self._last_input = monotonic()
        if autofocus:
            self.focus()

    def poll(self, input) -> None:
        if self.focused:
            input.poll_events(self.handle)

    def handle(self, e: str) -> bool:
        buf, c = self.text_buffer, self.cursor

        if e in ("\x7f", "\x08"):
            if c > 0:
                self.text_buffer, self.cursor = buf[:c - 1] + buf[c:], c - 1
        elif e == "delete":
            self.text_buffer = buf[:c] + buf[c + 1:]
        elif e == "left":
            self.cursor = max(0, c - 1)
        elif e == "right":
            self.cursor = min(len(buf), c + 1)
        elif e == "home":
            self.cursor = 0
        elif e == "end":
            self.cursor = len(buf)
        elif e in ("\r", "\n"):
            self.submitted_text = buf
            if self.clear_text_on_submit:
                self.text_buffer = ""
                self.cursor = 0
            if self.onSubmit:
                self.onSubmit(buf)
        elif len(e) == 1 and e.isprintable():
            if len(buf) < self.max_chars:
                self.text_buffer = buf[:c] + e + buf[c:]
                self.cursor = c + 1
        else:
            return False

        self._last_input = monotonic()
        return True

    def focus(self) -> None:
        self.focused = True
        self._last_input = monotonic()

    def blur(self) -> None:
        self.focused = False

    def content_size(self) -> tuple[int, int]:
        return (len(self.prompt) + self.width + 1, 1)

    def _view(self) -> tuple[int, str]:
        offset = max(0, self.cursor - self.width)
        visible = self.text_buffer[offset:offset + self.width + 1]
        return offset, (MASK_CHAR * len(visible) if self.hidden else visible)

    def render(self) -> str:
        _, shown = self._view()
        return self.prompt + shown.ljust(self.width + 1)

    def cursor_cell(self) -> tuple[int, int, str] | None:
        if not self.focused:
            return None
        elapsed = monotonic() - self._last_input
        if elapsed % (self.blink_rate * 2) >= self.blink_rate:
            return None
        offset, shown = self._view()
        rel = self.cursor - offset
        col = len(self.prompt) + rel
        if col >= self.w:
            return None
        under = shown[rel] if rel < len(shown) else " "
        return self.x + col, self.y, under

    def paint(self, r) -> None:
        r.draw(self.x, self.y, self.render(), self.style, clip=self.rect)

        cell = self.cursor_cell()
        if cell:
            r.draw_cursor(*cell, clip=self.rect)

__all__ = ["TextInput"]