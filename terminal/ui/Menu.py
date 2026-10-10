from scheduler import RENDERER, INPUT
from typing import Callable
from terminal.ui.ComponentTypes import Drawable

class MenuItem:
    def __init__(
            self,
            label: str | Drawable,
            onSelect: Callable | None=None,
            onFocus: Callable | None=None,
            onBlur: Callable | None=None,
            selectable: bool=True
        ):
        assert isinstance(label, str) or hasattr(label, "render"), (
            f"label must be a str or have render(), got {type(label).__name__}"
        )
        self.label = label
        self.onSelect = onSelect
        self.onFocus = onFocus
        self.onBlur = onBlur
        self.selectable = selectable

    def text(self) -> str:
        return self.label if isinstance(self.label, str) else self.label.render()

    def handle(self, e: str) -> bool:
        fn = getattr(self.label, "handle", None)
        return bool(fn and fn(e))

    def cursor_cell(self) -> tuple[int, str] | None:
        fn = getattr(self.label, "cursor_cell", None)
        return fn() if fn else None

    def select(self) -> None:
        if self.onSelect:
            self.onSelect()

    def focus(self) -> None:
        fn = getattr(self.label, "focus", None)
        if fn:
            fn()
        if self.onFocus:
            self.onFocus()

    def blur(self) -> None:
        fn = getattr(self.label, "blur", None)
        if fn:
            fn()
        if self.onBlur:
            self.onBlur()


class Menu:
    def __init__(
        self,
        items: list[MenuItem],
        position: tuple[int, int]| None=None,
        anchor_point: tuple[int, int] | None=None,
        marker: str="> ",
        wrap: bool=True,
    ):
        self.items = [i if isinstance(i, MenuItem) else MenuItem(i) for i in items]
        assert any(i.selectable for i in self.items), "Menu needs at least one selectable item"

        self.position = position
        self.anchor_point = anchor_point
        self.marker = marker
        self.wrap = wrap

        self.index = self._first_selectable()
        self.controls = {
            "up": -1,
            "down": 1,
        }
        self.select_keys = ("\r", "\n")

    def _first_selectable(self) -> int:
        return next(i for i, it in enumerate(self.items) if it.selectable)

    def _last_selectable(self) -> int:
        return next(i for i in range(len(self.items) - 1, -1, -1) if self.items[i].selectable)

    def _step(self, i: int, step: int) -> int:
        n = len(self.items)
        start = i
        for _ in range(n):
            j = i + step
            if self.wrap:
                j %= n
            elif not 0 <= j < n:
                return start
            i = j
            if self.items[i].selectable:
                return i
        return start

    def move(self, delta: int) -> None:
        step = 1 if delta > 0 else -1
        i = self.index
        for _ in range(abs(delta)):
            i = self._step(i, step)
        self.set_index(i)

    def set_index(self, i: int) -> None:
        if i == self.index or not self.items[i].selectable:
            return
        self.items[self.index].blur()
        self.index = i
        self.items[i].focus()

    @property
    def selected(self) -> MenuItem:
        return self.items[self.index]

    def poll(self) -> None:
        INPUT.poll_events(self._handle)

    def _handle(self, e: str) -> None:
        if self.selected.handle(e):
            return

        if e in self.controls:
            self.move(self.controls[e])
        elif e == "home":
            self.set_index(self._first_selectable())
        elif e == "end":
            self.set_index(self._last_selectable())
        elif e in self.select_keys:
            self.selected.select()

    def draw(self) -> None:
        pad = " " * len(self.marker)
        lines = [
            (self.marker if i == self.index else pad) + item.text()
            for i, item in enumerate(self.items)
        ]

        box_width = max(len(line) for line in lines)
        box_height = len(lines)

        target_x, target_y = self.position
        anchor_x, anchor_y = self.anchor_point

        screen_x = int(RENDERER.width * target_x)
        screen_y = int(RENDERER.height * target_y)

        abs_x = screen_x - int(box_width * anchor_x)
        abs_y = screen_y - int(box_height * anchor_y)

        for row, line in enumerate(lines):
            RENDERER.draw(abs_x, abs_y + row, line.ljust(box_width))

        cell = self.selected.cursor_cell()
        if cell:
            col = abs_x + len(self.marker) + cell[0]
            y = abs_y + self.index
            if 0 <= y < RENDERER.height and 0 <= col < RENDERER.width:
                RENDERER.buffer[y][col] = f"\033[7m{cell[1]}\033[0m"