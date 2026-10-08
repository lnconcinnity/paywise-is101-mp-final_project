import time


class TextInput:
    def __init__(
        self,
        position,
        anchor_point,
        renderer,
        input,
        prompt="> ",
        width=20,
        max_chars=256,
        blink_rate=0.5,
        onSubmit=None,
        clear_text_on_submit=True,
        text_transformer=None,
    ):
        self.position = position
        self.anchor_point = anchor_point
        self.renderer = renderer
        self.input = input
        self.prompt = prompt
        self.width = width
        self.max_chars = max_chars
        self.blink_rate = blink_rate
        self.onSubmit = onSubmit
        self.clear_text_on_submit = clear_text_on_submit
        self.text_transformer = text_transformer

        self.text_buffer = ""
        self.cursor = 0
        self.submitted_text = ""
        self._last_input = time.monotonic()

    def poll(self):
        self.input.poll_events(self.handle)

    def handle(self, e):
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

        self._last_input = time.monotonic()
        return True

    def focus(self):
        self._last_input = time.monotonic()

    def _view(self):
        offset = max(0, self.cursor - self.width)
        visible = self.text_buffer[offset:offset + self.width]
        if self.text_transformer is not None:
            shown = self.text_transformer(visible)
            shown = shown[:len(visible)].ljust(len(visible))
        else:
            shown = visible
        return offset, shown

    def render(self):
        _, shown = self._view()
        return self.prompt + shown.ljust(self.width + 1)

    def cursor_cell(self):
        elapsed = time.monotonic() - self._last_input
        if elapsed % (self.blink_rate * 2) >= self.blink_rate:
            return None
        offset, shown = self._view()
        rel = self.cursor - offset
        col = len(self.prompt) + rel
        under = shown[rel] if rel < len(shown) else " "
        return col, under

    def draw(self):
        r = self.renderer
        line = self.render()
        x = int(r.width * self.position[0]) - int(len(line) * self.anchor_point[0])
        y = int(r.height * self.position[1]) - int(1 * self.anchor_point[1])

        r.draw(x, y, line)

        cell = self.cursor_cell()
        if cell:
            col = x + cell[0]
            if 0 <= y < r.height and 0 <= col < r.width:
                r.buffer[y][col] = f"\033[7m{cell[1]}\033[0m"