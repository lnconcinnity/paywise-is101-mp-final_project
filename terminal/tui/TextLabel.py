from terminal.tui.Drawable import Drawable
from typing import Optional

class TextLabel(Drawable):
    def __init__(
        self,
        text: str = "",
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: Optional[tuple[int, int]] = None,
    ):
        super().__init__(position, anchor_point, size)
        self.text = str(text)

    def set_text(self, new_text: str) -> None:
        self.text = str(new_text)

    def content_size(self) -> tuple[int, int]:
        return (len(self.text), 1)

    def render(self) -> str:
        return self.text

    def paint(self, r) -> None:
        r.draw(self.x, self.y, self.text[:self.w])

__all__ = ["TextLabel"]