from terminal import *
import app.pages as pages

def layout() -> Pagination:
    pagination: Pagination | None = None
    current_user : dict | None = None

    greeting = TextLabel("")
    home_menu = Menu([
        MenuItem("Log out", onSelect=lambda: pagination.goto("login")),
        MenuItem("Exit", onSelect=Scheduler.stop),
    ])
    home = Page(
        "home",
        StackLayout(
            greeting,
            home_menu,
            spacing=1,
            align="center",
            position=(0.5, 0.5),
            anchor_point=(0.5, 0.5),
        ),
    )

    def on_login(user: dict) -> None:
        greeting.set_text(f"Signed in as {user['username']} ({user['privileges']['role'].replace("_", " ").title()})")
        pagination.goto("home")
        match user.properties.role:
            case "hr_manager":
                pagination.goto("hr_manager_view")
            case "payroll_manager":
                pagination.goto("payroll_manager_view")
            case _:
                pagination.goto("employee_view")

    pagination = Pagination(
        pages.LoginPage(on_login), 
        pages.HumanResourcesPage(lambda: current_user, lambda: pagination)
    )
    return pagination