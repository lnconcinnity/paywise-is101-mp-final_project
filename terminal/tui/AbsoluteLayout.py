from terminal.tui.Drawable import Drawable

class AbsoluteLayout(Drawable):
    def __init__(
        self,
        *children: Drawable,
        position: tuple[float, float] = (0.0, 0.0),
        anchor_point: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        visible: bool = True,
    ):
        super().__init__(position, anchor_point, size, visible)
        self.add_children([*children])

    def measure(self, size: tuple[float, float]) -> tuple[int, int]:
        if self.size is not None:
            w, h = self.size
            return (min(w, size[0]), min(h, size[1]))
        return (size[0], size[1])

    def arrange(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        super().arrange(position, size)
        for c in self.children:
            if not c.visible:
                continue
            cw, ch = c.measure(size)
            px, py = c.position
            ax, ay = c.anchor_point
            c.arrange(
                (
                    position[0] + int(size[0] * px) - int(cw * ax),
                    position[1] + int(size[1] * py) - int(ch * ay),
                ),
                (cw, ch)
            )

__all__ = ["AbsoluteLayout"]