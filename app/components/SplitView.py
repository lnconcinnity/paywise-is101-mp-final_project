from terminal.tui.Drawable import Drawable
from terminal.tui.StackLayout import StackLayout

def SplitView(left: Drawable, detail: Drawable, gap: int = 4) -> StackLayout:
    slot = StackLayout(detail, size=detail.measure((10_000, 10_000)))
    return StackLayout(left, slot, orientation="horizontal", spacing=gap)

__all__ = ["SplitView"]