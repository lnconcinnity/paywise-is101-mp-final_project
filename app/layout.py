from terminal import *
import app.pages as pages

def layout() -> Pagination:
    pagination: Pagination | None = None
    current_user : dict | None = None

    greeting = TextLabel("")
    login_attempts = 0
    
    """
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
    """

    def increment_login_attempts():
        nonlocal login_attempts
        login_attempts += 1

    def logout():
        nonlocal login_attempts, current_user
        login_attempts = 0
        current_user = None
        pagination.goto("login")

    def on_login(user: dict) -> None:
        nonlocal current_user
        greeting.set_text(f"Signed in as {user['username']} ({user['properties']['role'].replace("_", " ").title()})")
        current_user = user
        match user['properties']['role']:
            case "hr_manager":
                pagination.goto("hr_manager_view")
            case "payroll_manager":
                pagination.goto("payroll_manager_view")
            case _:
                pagination.goto("employee_view")

    pagination = Pagination(
        pages.LoginPage(on_login, lambda: login_attempts, lambda: increment_login_attempts()), 
        pages.HumanResourcesPage(lambda: current_user, lambda: pagination, lambda: logout())
    )
    return pagination