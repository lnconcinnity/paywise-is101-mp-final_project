from terminal.ui.TextLabel import TextLabel
from terminal.ui.TextInput import TextInput
from terminal.ui.Menu import Menu, MenuItem
from terminal.router.Pagination import Page, Pagination
from typing import Callable
from scheduler import stop

def LoginPage(get_pagination: Callable[[], Pagination]) -> Page:
    pagination = get_pagination()

    username = TextInput(prompt="Username: ", clear_text_on_submit=False)
    password = TextInput(prompt="Password: ", clear_text_on_submit=False, text_transformer=lambda s: "*" * len(s))

    title_text = "Welcome to PayWise Employee CLI Portal"
    title = TextLabel(text=title_text, position=(0.4, 0.3), anchor_point=(0.5, 0.5))
    nav = Menu(items=[
        MenuItem(username),
        MenuItem(password),
        MenuItem("="*int(len(title_text)*0.85), selectable=False),
        MenuItem("Login", onSelect=lambda: stop()),
        MenuItem("Exit", onSelect=lambda: stop()),
    ], position=(0.39, 0.5), anchor_point=(0.5, 0.5))

    page = Page("login", nav, title)
    return page