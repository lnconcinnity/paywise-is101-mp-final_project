from typing import Optional
from terminal.tui.Drawable import Drawable

ALIGNS = ("start", "center", "end", "stretch")

class GridLayout(Drawable):
    def __init__(
        self,
        *children: Drawable,
        columns: int = 2,
        column_spacing: int = 1,
        row_spacing: int = 0,
        align: str = "start",
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: Optional[tuple[int, int]] = None,
        visible: bool = True,
    ):
        super().__init__(position, anchor_point, size, visible)
        assert columns >= 1, f"columns must be at least 1, got {columns}"
        assert align in ALIGNS, f"align must be one of {ALIGNS}, got {align!r}"
        self.columns = columns
        self.column_spacing = column_spacing
        self.row_spacing = row_spacing
        self.align = align
        self.add_children([*children])

    def _rows(self) -> list[list[Drawable]]:
        return [
            self.children[i:i + self.columns]
            for i in range(0, len(self.children), self.columns)
        ]

    def _tracks(self, max_size: tuple[float, float]):
        rows = self._rows()
        widths = [0] * min(self.columns, len(self.children))
        heights = [0] * len(rows)
        for r, row in enumerate(rows):
            for c, child in enumerate(row):
                if not child.visible:
                    continue
                w, h = child.measure(max_size)
                widths[c] = max(widths[c], w)
                heights[r] = max(heights[r], h)
        return rows, widths, heights

    def measure(self, max_size: tuple[float, float]) -> tuple[int, int]:
        if self.size is not None:
            w, h = self.size
            return (min(w, max_size[0]), min(h, max_size[1]))

        rows, widths, heights = self._tracks(max_size)
        if not rows:
            return (0, 0)

        w = sum(widths) + self.column_spacing * (len(widths) - 1)
        h = sum(heights) + self.row_spacing * (len(heights) - 1)
        return (min(w, max_size[0]), min(h, max_size[1]))

    def arrange(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        super().arrange(position, size)
        rows, widths, heights = self._tracks(size)
        right = position[0] + size[0]
        bottom = position[1] + size[1]

        y = position[1]
        for r, row in enumerate(rows):
            row_h = max(0, min(heights[r], bottom - y))
            x = position[0]
            for c, child in enumerate(row):
                col_w = max(0, min(widths[c], right - x))
                if child.visible:
                    cw, ch = child.measure((col_w, row_h))
                    if self.align == "stretch":
                        cw = col_w
                    offset = {
                        "start": 0,
                        "stretch": 0,
                        "center": (col_w - cw) // 2,
                        "end": col_w - cw,
                    }[self.align]
                    child.arrange((x + offset, y), (cw, ch))
                x += col_w + self.column_spacing
            y += row_h + self.row_spacing

__all__ = ["GridLayout"]