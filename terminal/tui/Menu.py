from typing import Callable, Optional
from terminal.tui.Selection import Selection
from terminal.tui.Drawable import Drawable
from terminal.tui.StackLayout import StackLayout
from terminal.tui.TextLabel import TextLabel

class MenuItem(StackLayout):
    def __init__(
        self,
        content: str | Drawable,
        onSelect: Optional[Callable] = None,
        onFocus: Optional[Callable] = None,
        onBlur: Optional[Callable] = None,
        selectable: bool = True,
    ):
        if isinstance(content, str):
            content = TextLabel(content)
        assert isinstance(content, Drawable), (
            f"content must be a str or a Drawable, got {type(content).__name__}"
        )
        self.marker = TextLabel("")
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
        size: Optional[tuple[int, int]] = None,
        marker: str = "> ",
        wrap: bool = True,
        spacing: int = 0,
        align: str = "start",
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
        self.sel = Selection(
            lambda: len(self.items),
            wrap=wrap,
            skip=lambda i: not self.items[i].selectable,
            on_change=self._on_change,
        )
        self.controls = {"up": -1, "down": 1}
        self.select_keys = ("\r", "\n")

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

    def move(self, delta: int) -> None:
        self.sel.step(delta)

    def set_index(self, i: int) -> None:
        self.sel.set(i)

    def _on_change(self, old: int, new: int) -> None:
        self.items[old].blur()
        self.items[new].focus()
        self._refresh_markers()

    def _refresh_markers(self) -> None:
        pad = " " * len(self.marker)
        for i, item in enumerate(self.items):
            item.marker.set_text(self.marker if i == self.sel.index else pad)

    def poll(self, input) -> None:
        input.poll_events(self._handle)

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