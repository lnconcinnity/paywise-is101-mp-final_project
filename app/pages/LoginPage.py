from typing import Callable

from erp import users
from terminal import *

def LoginPage(on_login: Callable[[dict], None]) -> Page:
    TITLE = "Welcome to PayWise Employee CLI Portal"

    username = TextInput(prompt="Username: ", clear_text_on_submit=False)
    password = TextInput(prompt="Password: ", clear_text_on_submit=False, hidden=True)
    status = TextLabel("", size=(len(TITLE), 1))

    def attempt() -> None:
        _, user = users.find(
            lambda u: u["username"] == username.text_buffer
            and u["password"] == password.text_buffer
        )
        if user is None:
            status.set_text("Invalid username or password.")
            return
        status.set_text("")
        for field in (username, password):
            field.text_buffer, field.cursor = "", 0
        on_login(user)

    username.onSubmit = lambda _: menu.move(1)
    password.onSubmit = lambda _: attempt()

    menu = Menu([
        MenuItem(username),
        MenuItem(password),
        MenuItem("=" * int(len(TITLE) * 0.85), selectable=False),
        MenuItem("Login", onSelect=attempt),
        MenuItem("Exit", onSelect=Scheduler.stop),
    ])

    card = StackLayout(
        TextLabel(TITLE),
        menu,
        status,
        orientation="vertical",
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )

    hints = StackLayout(
        TextLabel("Up/Down: move"),
        TextLabel("Enter: select"),
        orientation="horizontal",
        spacing=3,
        position=(0.5, 1.0),
        anchor_point=(0.5, 1.0),
    )

    return Page("login", card, hints)

__all__ = ["LoginPage"]