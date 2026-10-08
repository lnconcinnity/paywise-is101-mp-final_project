from terminal.ui.TextLabel import TextLabel
from terminal.ui.TextInput import TextInput
from terminal.ui.Menu import Menu, MenuItem

def layout():
    return Menu(items=[
        MenuItem("Create Account"),
        MenuItem("Login"),
        MenuItem(TextInput(prompt="Your Name:", clear_text_on_submit=False, text_transformer=lambda s: "*" * len(s))),
        MenuItem("Exit", onSelect=exit),
    ], position=(0.5, 0.5), anchor_point=(0.5,0.5),)