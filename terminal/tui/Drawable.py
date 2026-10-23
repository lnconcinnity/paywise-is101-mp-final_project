from __future__ import annotations
from typing import Iterable

class Drawable:
    focusable: bool = False
    def __init__(
        self,
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: tuple[float, float] | None = None,
        visible: bool = True,
    ):
        self.position = position
        self.anchor_point = anchor_point
        self.size = size
        self.visible = visible

        self.x = self.y = self.w = self.h = 0
 
        self.parent: Drawable | None = None
        self.children: list[Drawable] = []

    # ancestry handling
    def add_child(self, child: Drawable) -> Drawable:
        child.parent = self
        self.children.append(child)
        return self

    def add_children(self, children: list[Drawable]) -> Drawable:
        for child in children:
            self.add_child(child)
        return self

    def remove_child(self, child: Drawable) -> Drawable:
        self.children.remove(child)
        child.parent = None
        return self

    def walk(self) -> Iterable[Drawable]:
        yield self
        for child in self.children:
            yield from child.walk()

    # bounding box methods
    def content_size(self) -> tuple[float, float]:
        return (0, 0)

    def measure(self, max_size: tuple[float, float]) -> tuple[float, float]:
        w, h = self.size if self.size is not None else self.content_size()
        return (min(w, max_size[0]), min(h, max_size[1]))

    def arrange(self, position: tuple[float, float], size: tuple[float, float]):
        self.x, self.y = position
        self.w, self.h = size

    @property
    def rect(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    def contains_point(self, point: tuple[float, float]) -> bool:
        x, y = point
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    # lifecycle
    def poll(self, input) -> None:
        for child in self.children:
            child.poll(input)

    def draw(self, renderer, offset: tuple[float, float] = (0.0, 0.0)) -> None:
        if not self.visible:
            return
        self.paint(renderer)
        for child in self.children:
            child.draw(renderer)

    # components should override this method to implement their own painting logic
    def paint(self, renderer):
        pass

    # event handling methods should be overridden by subclasses to handle specific events
    def handle(self, e: str) -> bool:
        return False
    def focus(self) -> None: ...
    def blur(self) -> None: ...

    # unique to text input components, this method should return the current cursor position in the text input, or None if there is no cursor
    def cursor_cell(self) -> tuple[int, int] | None:
        return None