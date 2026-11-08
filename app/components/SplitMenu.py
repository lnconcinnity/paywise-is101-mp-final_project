from dataclasses import dataclass, field
from typing import Callable
from terminal import *
from app.components.SplitView import SplitView

@dataclass
class Entry:
    label: str
    on_select: Callable[[], None]
    preview: list[str] = field(default_factory=list)
    style: tuple[int, ...] = field(default_factory=tuple)

def SplitMenu(
    entries: list[Entry],
    footer: list[tuple[str, Callable[[], None]], tuple[int, ...]] | None = None,
    on_focus: Callable[[], None] | None = None,
    gap: int = 4,
) -> tuple[StackLayout, Callable[[], None]]:
    footer = footer or []
    rows = max([len(entry.preview) for entry in entries] + [0])
    width = max(
        [len(entry.label) for entry in entries]
        + [len(line) for entry in entries for line in entry.preview]
        + [0]
    )
    heading = TextLabel("", size=(width, 1), style=(BOLD,))
    body = [TextLabel("", size=(width, 1)) for _ in range(rows)]

    def show(entry: Entry | None) -> None:
        heading.set_text(entry.label if entry else "")
        lines = entry.preview if entry else []
        for i, label in enumerate(body):
            label.set_text(lines[i] if i < len(lines) else "")
        if on_focus:
            on_focus()

    items = [
        MenuItem(entry.label, style=entry.style, onSelect=entry.on_select, onFocus=lambda e=entry: show(e))
        for entry in entries
    ]
    if entries and footer:
        items.append(MenuItem("=" * max(len(entry.label) for entry in entries), style=(DIM,), selectable=False))
    items += [MenuItem(label, style=style, onSelect=action, onFocus=lambda: show(None)) for label, action, style in footer]
    menu = Menu(items)

    layout = SplitView(menu, StackLayout(heading, *body), gap)

    def reset() -> None:
        menu.blur()
        menu.set_index(menu.sel.first())
        menu.focus()

    reset()
    return layout, reset

__all__ = ["Entry", "SplitMenu"]