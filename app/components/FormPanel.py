from dataclasses import dataclass
from typing import Callable
from terminal import *

@dataclass(frozen=True)
class Text:
    key: str
    label: str
    hidden: bool = False
    default: str = ""
    style: tuple[int, ...] = ()
    width: int = 18

@dataclass(frozen=True)
class Choice:
    key: str
    label: str
    options: tuple[str, ...]

Field = Text | Choice
Result = tuple[bool, list[str]]

class FormPanel(StackLayout):
    def __init__(
        self,
        title: str,
        fields: list[Field],
        submit: str,
        on_submit: Callable[[dict[str, str]], Result],
        on_back: Callable[[], None],
        width: int = 44,
        rows: int = 2,
        keep_on_success: bool = False,
        side: bool = False,
        style: tuple[int, ...] = (),
    ):
        label_w = max(len(f.label) for f in fields)
        self._fields = fields
        self._label_w = label_w
        self._width = width
        self._on_submit = on_submit
        self._keep = keep_on_success
        self._inputs: dict[str, TextInput] = {}
        self._choice_at: dict[str, int] = {}
        self._choice_label: dict[str, TextLabel] = {}

        items: list[MenuItem] = []
        for f in fields:
            if isinstance(f, Text):
                box = TextInput(style=f.style,prompt=f"{f.label.ljust(label_w)} : ", width=f.width, hidden=f.hidden, clear_text_on_submit=False)
                box.onSubmit = self._on_enter if f is fields[-1] else (lambda _: self._menu.move(1))
                self._inputs[f.key] = box
                items.append(MenuItem(box))
            else:
                opt_w = max(len(o) for o in f.options)
                label = TextLabel("", size=(label_w + 3 + opt_w + 4, 1))
                self._choice_at[f.key] = 0
                self._choice_label[f.key] = label
                items.append(MenuItem(label, onSelect=lambda c=f: self._cycle(c)))

        items.append(MenuItem("=" * (label_w + 3 + max(f.width if isinstance(f, Text) else 0 for f in fields)), style=(DIM,), selectable=False))
        items.append(MenuItem(submit, onSelect=self._submit, style=style))
        items.append(MenuItem("Back", style=(DIM,), onSelect=on_back))

        self._menu = Menu(items, autofocus=False)
        self._results = [TextLabel("", size=(width, 1)) for _ in range(rows)]
        head = TextLabel(title, style=(BOLD,))
        if side:
            super().__init__(
                StackLayout(head, self._menu, spacing=1),
                StackLayout(*self._results),
                orientation="horizontal",
                spacing=4,
            )
        else:
            super().__init__(head, self._menu, StackLayout(*self._results), spacing=1)
        self._reset_fields()

    def _on_enter(self, _text: str) -> None:
        self._submit()

    def _values(self) -> dict[str, str]:
        values = {}
        for f in self._fields:
            if isinstance(f, Text):
                values[f.key] = self._inputs[f.key].text_buffer.strip()
            else:
                values[f.key] = f.options[self._choice_at[f.key]]
        return values

    def _refresh(self, c: Choice) -> None:
        shown = c.options[self._choice_at[c.key]]
        self._choice_label[c.key].set_text(f"{c.label.ljust(self._label_w)} : < {shown} >")

    def _cycle(self, c: Choice) -> None:
        self._choice_at[c.key] = (self._choice_at[c.key] + 1) % len(c.options)
        self._refresh(c)

    def _reset_fields(self) -> None:
        for f in self._fields:
            if isinstance(f, Text):
                box = self._inputs[f.key]
                box.text_buffer = f.default
                box.cursor = len(f.default)
            else:
                self._choice_at[f.key] = 0
                self._refresh(f)
        self._menu.set_index(self._menu.sel.first())

    def _show(self, ok: bool, lines: list[str]) -> None:
        style = (BRIGHT_GREEN,) if ok else (BRIGHT_RED,)
        for i, label in enumerate(self._results):
            label.style = style
            label.set_text(lines[i][: self._width] if i < len(lines) else "")

    def _submit(self) -> None:
        ok, lines = self._on_submit(self._values())
        self._show(ok, lines)
        if ok and not self._keep:
            self._reset_fields()

    def open(self) -> None:
        self._reset_fields()
        self._show(True, [])
        self.visible = True
        self._menu.focus()

    def close(self) -> None:
        self._menu.blur()
        self.visible = False

__all__ = ["FormPanel", "Text", "Choice"]