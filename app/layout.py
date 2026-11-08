from app.modules.UserRecord import UserRecord
from terminal import *
from app.modules.GlobalStore import use_store
import app.pages as pages

def layout() -> Pagination:
    def on_login(user: UserRecord) -> None:
        use_store.set("current_user", user)
        pagination.goto("navigation")

    pagination = Pagination(
        pages.LoginPage(),
        pages.NavigationPage(),
        pages.EmployeeRecordsPage(),
        pages.TimeTrackingPage(),
    )
    use_store.set("pagination", pagination)
    return pagination