from terminal.tui.Drawable import Drawable

VERTICAL = "vertical"
HORIZONTAL = "horizontal"
ALIGNS = ("start", "center", "end", "stretch")

class StackLayout(Drawable):
    def __init__(
        self,
        *children: Drawable,
        orientation: str = VERTICAL,
        spacing: int = 0,
        align: str = "start",
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        visible: bool = True,
    ):
        super().__init__(position, anchor_point, size, visible)
        assert orientation in (VERTICAL, HORIZONTAL), (
            f"orientation must be 'vertical' or 'horizontal', got {orientation!r}"
        )
        assert align in ALIGNS, f"align must be one of {ALIGNS}, got {align!r}"
        self.orientation = orientation
        self.spacing = spacing
        self.align = align
        self.add_children([*children])

    @property
    def _horizontal(self) -> bool:
        return self.orientation == HORIZONTAL

    def _shown(self) -> list[Drawable]:
        return [c for c in self.children if c.visible]

    def measure(self, size: tuple[float, float]) -> tuple[int, int]:
        if self.size is not None:
            w, h = self.size
            return (min(w, size[0]), min(h, size[1]))

        kids = self._shown()
        if not kids:
            return (0, 0)

        sizes = [c.measure(size) for c in kids]
        gaps = self.spacing * (len(kids) - 1)
        if self._horizontal:
            w, h = sum(s[0] for s in sizes) + gaps, max(s[1] for s in sizes)
        else:
            w, h = max(s[0] for s in sizes), sum(s[1] for s in sizes) + gaps
        return (min(w, size[0]), min(h, size[1]))

    def arrange(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        super().arrange(position, size)
        horiz = self._horizontal
        main_total, cross_total = (size[0], size[1]) if horiz else (size[1], size[0])

        pos = 0
        for c in self._shown():
            remaining = max(0, main_total - pos)
            cw, ch = c.measure((remaining, cross_total)) if horiz else c.measure((cross_total, remaining))
            main, cross = (cw, ch) if horiz else (ch, cw)

            if self.align == "stretch":
                cross = cross_total
            offset = {
                "start": 0,
                "stretch": 0,
                "center": (cross_total - cross) // 2,
                "end": cross_total - cross,
            }[self.align]

            if horiz:
                c.arrange((position[0] + pos, position[1] + offset), (main, cross))
            else:
                c.arrange((position[0] + offset, position[1] + pos), (cross, main))
            pos += main + self.spacing

__all__ = ["StackLayout", "VERTICAL", "HORIZONTAL", "ALIGNS"]