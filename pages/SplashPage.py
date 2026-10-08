from terminal.ui.Pagination import Pagination, Page
from terminal.ui.TextInput import TextInput
from terminal.ui.TextLabel import TextLabel
from terminal.ui.Menu import Menu, MenuItem

def page(renderer, input, get_parent):
    menu = Menu(
        position=(0.5, 0.5), anchor_point=(0.5, 0.5),
        items=[
            MenuItem("Login", lambda: get_parent().goto("login")), 
            MenuItem("Exit", exit)
        ],
        renderer=renderer,
        input=input
    )
    
    return Page("splash", menu)