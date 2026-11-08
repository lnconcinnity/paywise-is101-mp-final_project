from typing import Any, Callable
from terminal import *
from app.components.SplitView import SplitView
from app.modules.GlobalStore import use_store

MAX_LOGIN_ATTEMPTS = 3

def LoginPage() -> Page:
    title = TextLabel("PayWise CLI", style=(BOLD, UNDERLINE, BRIGHT_BLUE))
    entries = {
        entry["account"].name: entry
        for entry in (use_store.get("user_accounts") or {}).values()
        if not entry["account"].deactivated
    }
    names = list(entries)

    inner_width = max(
        [len("Invalid password.")]
        + [len(f"Sign in as {name}?") for name in names]
        + [len(f"{name} is locked.") for name in names]
    )
    header = TextLabel("", size=(inner_width, 1))
    status = TextLabel("", size=(inner_width, 1), style=(RED,))
    password = TextInput(prompt="Password: ", clear_text_on_submit=False, hidden=True, style=(BRIGHT_BLUE,))

    account: str | None = None

    def clear_password() -> None:
        password.text_buffer = ""
        password.cursor = 0

    def reset_form() -> None:
        clear_password()
        status.set_text("")
        form.set_index(form.sel.first())

    def hide_form() -> None:
        form.blur()
        reset_form()
        form.visible = False

    def show_preview(name: str) -> None:
        nonlocal account
        account = name
        locked = entries[name]["security"]["locked"]
        header.set_text(f"{name} is locked." if locked else f"Sign in as {name}?")
        hide_form()
        panel.visible = True

    def hide_panel() -> None:
        nonlocal account
        account = None
        hide_form()
        panel.visible = False

    def sign_in(entry: dict) -> None:
        entry["security"]["login_attempts"] = 0
        use_store.set("current_user", entry["account"])
        use_store.get("pagination").goto("navigation")

    def enter_form() -> None:
        entry = entries[account]
        if entry["security"]["locked"]:
            return
        if entry["account"].passwordless:
            sign_in(entry)
            return
        reset_form()
        form.visible = True
        left.blur()
        form.focus()

    def back() -> None:
        form.blur()
        left.focus()

    def attempt() -> None:
        entered = password.text_buffer
        clear_password()
        entry = entries[account]
        security = entry["security"]
        if entry["account"].authenticate(entered):
            sign_in(entry)
            return
        security["login_attempts"] += 1
        if security["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
            security["locked"] = True
            back()
            return
        status.set_text("Invalid password.")

    def reset_page() -> None:
        form.blur()
        left.blur()
        left.focus()

    password.onSubmit = lambda _: attempt()

    form = Menu([
        MenuItem(password),
        MenuItem("=" * inner_width, selectable=False, style=(DIM,)),
        MenuItem("Login", onSelect=attempt, style=(BRIGHT_YELLOW, BOLD)),
        MenuItem("Back", onSelect=back, style=(DIM,)),
        MenuItem(status, selectable=False),
    ], autofocus=False)

    items = [
        MenuItem(name, onSelect=enter_form, onFocus=lambda n=name: show_preview(n))
        for name in names
    ]
    if names:
        items.append(MenuItem("=" * max(len(name) for name in names), style=(DIM,), selectable=False))
    items.append(MenuItem("Exit", style=(BOLD, BRIGHT_RED), onSelect=Scheduler.stop, onFocus=hide_panel))
    left = Menu(items)

    panel = StackLayout(header, form, spacing=1)
    split = SplitView(left, panel)
    stack = StackLayout(
        title,
        split,
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )

    reset_page()
    return Page(stack, name="login", onEnter=reset_page)

__all__ = ["LoginPage"]