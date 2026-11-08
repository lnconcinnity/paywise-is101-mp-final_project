from typing import Callable
from terminal.tui.Selection import Selection
from terminal.tui.Drawable import Drawable
from terminal.tui.StackLayout import StackLayout
from terminal.tui.TextLabel import TextLabel
from terminal.colors import DIM

class MenuItem(StackLayout):
    def __init__(
        self,
        content: str | Drawable,
        onSelect: Callable | None = None,
        onFocus: Callable | None = None,
        onBlur: Callable | None = None,
        selectable: bool = True,
        style: tuple[int, ...] = ()
    ):
        if isinstance(content, str):
            content = TextLabel(content, style=style)
        assert isinstance(content, Drawable), (
            f"content must be a str or a Drawable, got {type(content).__name__}"
        )
        self.marker = TextLabel("", style=(DIM,))
        self.content = content
        super().__init__(self.marker, content, orientation="horizontal")

        self.onSelect = onSelect
        self.onFocus = onFocus
        self.onBlur = onBlur
        self.selectable = selectable

    def handle(self, e: str) -> bool:
        return self.content.handle(e)

    def select(self) -> None:
        if self.onSelect:
            self.onSelect()

    def focus(self) -> None:
        self.content.focus()
        if self.onFocus:
            self.onFocus()

    def blur(self) -> None:
        self.content.blur()
        if self.onBlur:
            self.onBlur()


class Menu(StackLayout):
    def __init__(
        self,
        items: list[MenuItem | str | Drawable],
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        marker: str = "> ",
        wrap: bool = True,
        spacing: int = 0,
        align: str = "start",
        autofocus: bool = True,
    ):
        items = [i if isinstance(i, MenuItem) else MenuItem(i) for i in items]
        super().__init__(
            *items,
            orientation="vertical",
            spacing=spacing,
            align=align,
            position=position,
            anchor_point=anchor_point,
            size=size,
        )
        assert any(i.selectable for i in self.items), "Menu needs at least one selectable item"

        self.marker = marker
        self.focused = False
        self.sel = Selection(
            lambda: len(self.items),
            wrap=wrap,
            skip=lambda i: not self.items[i].selectable,
            on_change=self._on_change,
        )
        self.controls = {"up": -1, "down": 1}
        self.select_keys = ("\r", "\n")

        if autofocus:
            self.focused = True
            self.selected.content.focus()
        self._refresh_markers()

    @property
    def items(self) -> list[MenuItem]:
        return self.children

    @property
    def index(self) -> int:
        return self.sel.index

    @property
    def selected(self) -> MenuItem:
        return self.items[self.sel.index]

    def focus(self) -> None:
        if self.focused:
            return
        self.focused = True
        self.selected.focus()
        self._refresh_markers()

    def blur(self) -> None:
        if not self.focused:
            return
        self.selected.blur()
        self.focused = False
        self._refresh_markers()

    def move(self, delta: int) -> None:
        self.sel.step(delta)

    def set_index(self, i: int) -> None:
        self.sel.set(i)

    def _on_change(self, old: int, new: int) -> None:
        if self.focused:
            self.items[old].blur()
            self.items[new].focus()
        self._refresh_markers()

    def _refresh_markers(self) -> None:
        pad = " " * len(self.marker)
        for i, item in enumerate(self.items):
            shown = self.focused and i == self.sel.index
            item.marker.set_text(self.marker if shown else pad)

    def _update_offset(self, available: float) -> None:
        shown = self._shown()
        if not shown:
            self.offset = 0
            return
        heights = [item.measure((10_000, 10_000))[1] for item in shown]

        def span(first: int, stop: int) -> int:
            part = heights[first:stop]
            return sum(part) + self.spacing * max(0, len(part) - 1)

        offset = max(0, min(self.offset, len(shown) - 1))
        if self.selected in shown:
            selected = shown.index(self.selected)
            offset = min(offset, selected)
            while offset < selected and span(offset, selected + 1) > available:
                offset += 1
        while offset > 0 and span(offset - 1, len(shown)) <= available:
            offset -= 1
        self.offset = offset

    def arrange(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        self._update_offset(size[1])
        super().arrange(position, size)

    def poll(self, input) -> None:
        if not self.focused:
            return
        consumed = 0

        def feed(e: str) -> None:
            nonlocal consumed
            if self.focused:
                consumed += 1
                self._handle(e)

        input.poll_events(feed)
        del input.frame_events[:consumed]

    def _handle(self, e: str) -> None:
        if self.selected.handle(e):
            return

        if e in self.controls:
            self.move(self.controls[e])
        elif e == "home":
            self.sel.set(self.sel.first())
        elif e == "end":
            self.sel.set(self.sel.last())
        elif e in self.select_keys:
            self.selected.select()

__all__ = ["Menu", "MenuItem"]