from terminal.ui.TextLabel import TextLabel
from terminal.ui.Menu import Menu, MenuItem
from scheduler import RENDERER, INPUT

def layout():
    return Menu(items=[
        MenuItem("Create Account"),
        MenuItem("Login"),
        MenuItem("Exit", onSelect=exit),
    ], position=(0.5, 0.5), anchor_point=(0.5,0.5),)