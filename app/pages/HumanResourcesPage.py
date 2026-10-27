from typing import Callable

from erp import users
from terminal import *

def HumanResourcesPage(get_current_user, get_pagination, logout):
    TITLE = "Human Resources Manager View"
    menu = Menu([
        MenuItem("Employee Records"),
        MenuItem("Employee Attendance"),
        MenuItem("=" * int(len(TITLE) * 0.85), selectable=False),
        MenuItem("Logout", onSelect=logout),
        MenuItem("Exit", onSelect=Scheduler.stop),
    ])
    card = StackLayout(
        TextLabel(TITLE),
        menu,
        orientation="vertical",
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )
    return Page("hr_manager_view", card)


__all__ = ['HumanResourcesPage']