from typing import Callable

from terminal.tui.Selection import Selection
from terminal.tui.AbsoluteLayout import AbsoluteLayout
from terminal.tui.Drawable import Drawable


class Page(AbsoluteLayout):
    def __init__(
        self,
        *widgets: Drawable,
        name: str,
        onEnter: Callable | None = None,
        onExit: Callable | None = None,
    ):
        super().__init__(*widgets)
        self.name = name
        self.onEnter = onEnter
        self.onExit = onExit

    @property
    def widgets(self) -> list[Drawable]:
        return self.children

    def enter(self) -> None:
        if self.onEnter:
            self.onEnter()

    def exit(self) -> None:
        if self.onExit:
            self.onExit()


class Pagination(Drawable):
    def __init__(self, *pages: Page, wrap: bool = False):
        assert pages, "Pagination needs at least one Page"
        for p in pages:
            assert isinstance(p, Page), f"expected Page, got {type(p).__name__}"

        names = [p.name for p in pages]
        assert len(set(names)) == len(names), f"duplicate page names: {names}"

        super().__init__()
        self.add_children([*pages])
        self.wrap = wrap
        self._by_name = {p.name: i for i, p in enumerate(pages)}
        self.sel = Selection(
            lambda: len(self.pages), wrap=wrap, on_change=self._on_change
        )

        self.current.enter()

    @property
    def pages(self) -> list[Page]:
        return self.children

    @property
    def index(self) -> int:
        return self.sel.index

    @property
    def current(self) -> Page:
        return self.pages[self.sel.index]

    def _on_change(self, old: int, new: int) -> None:
        self.pages[old].exit()
        self.pages[new].enter()

    def goto(self, target: str | int) -> bool:
        if isinstance(target, str):
            if target not in self._by_name:
                raise KeyError(
                    f"unknown page {target!r}; known pages: {list(self._by_name)}"
                )
            i = self._by_name[target]
        else:
            if not 0 <= target < len(self.pages):
                raise IndexError(
                    f"page index {target} out of range (0..{len(self.pages) - 1})"
                )
            i = target
        return self.sel.set(i)

    def next(self) -> bool:
        return self.sel.step(1)

    def back(self) -> bool:
        return self.sel.step(-1)

    def measure(self, size: tuple[float, float]) -> tuple[int, int]:
        return size

    def arrange(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        super().arrange(position, size)
        self.current.arrange(position, size)

    def poll(self, input) -> None:
        self.current.poll(input)

    def draw(self, r) -> None:
        if self.visible:
            self.paint(r)
            self.current.draw(r)

__all__ = ["Pagination", "Page"]