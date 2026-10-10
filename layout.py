from terminal.ui.TextLabel import TextLabel
from terminal.ui.TextInput import TextInput
from terminal.ui.Menu import Menu, MenuItem
from terminal.router.Pagination import Pagination

from pages import *

def layout():
    pagination: Pagination | None = None
    pagination = Pagination(
        LoginPage(lambda: pagination)
    )
    return pagination