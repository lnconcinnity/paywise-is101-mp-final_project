from terminal import *
from app.components.FormPanel import FormPanel
from app.components.EmployeeForms import add_form, view_form, search_form, deactivate_form
from app.components.Navigation import go_home

SPECS = [
    ("Add New Employee", add_form, ["Register a new employee account.", "Enter cycles a choice."]),
    ("View Employee", view_form, ["Find by first name, last name", "or username."]),
    ("Search Filter", search_form, ["Filter by department,", "category or status."]),
    ("Deactivate Employee", deactivate_form, ["Disable an employee's account."]),
]

def EmployeeRecordsPage() -> Page:
    title = TextLabel("Employee Records", style=(BOLD, UNDERLINE, BRIGHT_BLUE))

    width = max(len(label) for label, _, _ in SPECS)
    width = max([width] + [len(line) for _, _, lines in SPECS for line in lines])
    rows = max(len(lines) for _, _, lines in SPECS)
    heading = TextLabel("", size=(width, 1), style=(BOLD,))
    body = [TextLabel("", size=(width, 1)) for _ in range(rows)]
    preview = StackLayout(heading, *body)
    descriptions = {label: lines for label, _, lines in SPECS}

    active: FormPanel | None = None

    def show(label: str | None) -> None:
        heading.set_text(label or "")
        lines = descriptions.get(label, [])
        for i, row in enumerate(body):
            row.set_text(lines[i] if i < len(lines) else "")
        preview.visible = True

    def back() -> None:
        nonlocal active
        if active:
            active.close()
            active = None
        left.focus()

    forms = {label: build(back) for label, build, _ in SPECS}

    def opener(label: str):
        def action() -> None:
            nonlocal active
            active = forms[label]
            preview.visible = False
            left.blur()
            active.open()
        return action

    items = [
        MenuItem(label, onSelect=opener(label), onFocus=lambda l=label: show(l))
        for label, _, _ in SPECS
    ]
    items.append(MenuItem("=" * max(len(label) for label, _, _ in SPECS), style=(DIM,), selectable=False))
    items.append(MenuItem("Back", style=(BRIGHT_RED,), onSelect=go_home, onFocus=lambda: show(None)))
    left = Menu(items)

    sizes = [d.measure((10_000, 10_000)) for d in (preview, *forms.values())]
    slot = StackLayout(preview, *forms.values(), size=(max(s[0] for s in sizes), max(s[1] for s in sizes)))
    for form in forms.values():
        form.close()

    stack = StackLayout(
        title,
        StackLayout(left, slot, orientation="horizontal", spacing=4),
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )

    def reset() -> None:
        nonlocal active
        for form in forms.values():
            form.close()
        active = None
        left.blur()
        left.set_index(left.sel.first())
        left.focus()

    reset()
    return Page(stack, name="employee_records", onEnter=reset)

__all__ = ["EmployeeRecordsPage"]