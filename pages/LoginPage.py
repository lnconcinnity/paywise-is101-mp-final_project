from terminal.ui.Pagination import Pagination, Page
from terminal.ui.TextInput import TextInput
from terminal.ui.TextLabel import TextLabel
from terminal.ui.Menu import Menu, MenuItem

def page(renderer, input, get_parent):
    menu = None
    get_menu = lambda: menu

    name = TextInput(
        None,
        None,
        renderer,
        input,
        prompt="Name: ",
        onSubmit=lambda t: get_menu().move(1),
        clear_text_on_submit=False
    )
    
    password = TextInput(
        None,
        None,
        renderer,
        input,
        prompt="Password: ",
        onSubmit=lambda t: get_menu().move(1),
        clear_text_on_submit=False,
        text_transformer=lambda s: "*" * len(s)
    )

    menu = Menu(
        position=(0.5, 0.5), anchor_point=(0.5, 0.5),
        items=[
            MenuItem(name),
            MenuItem(password),
            MenuItem("Back", onSelect=lambda: get_parent().goto("splash"))
        ],
        renderer=renderer,
        input=input
    )
    
    return Page("login", menu)