from dataclasses import dataclass, field
from app.modules.GlobalStore import use_store

@dataclass(frozen=True)
class Section:
    label: str
    page: str
    actions: tuple[str, ...] = field(default_factory=tuple)

EMPLOYEE_ACTIONS = (
    "Add New Employee",
    "View Employee",
    "Search Filter",
    "Deactivate Employee",
)

TIME_ACTIONS = (
    "Log weekly hours",
    "File paid leave",
)

SECTIONS: dict[str, tuple[Section, ...]] = {
    "hr_manager": (
        Section("Employee Records", "employee_records", EMPLOYEE_ACTIONS),
        Section("Time Tracking", "time_tracking", TIME_ACTIONS),
    ),
    "payroll_manager": (
        Section("Salary & Overtime Compensation", "salary_overtime"),
        Section("Payroll Generation", "payroll_generation"),
        Section("Reports & Period Locking", "reports_period_locking"),
    ),
}

ROLE_TITLES = {
    "hr_manager": "HR Manager",
    "payroll_manager": "Payroll Manager",
}

def navigate(name: str) -> bool:
    try:
        use_store.get("pagination").goto(name)
    except KeyError:
        return False
    return True

def go_home() -> None:
    if use_store.get("current_user") is None or not navigate("navigation"):
        navigate("login")

__all__ = ["Section", "SECTIONS", "EMPLOYEE_ACTIONS", "TIME_ACTIONS", "ROLE_TITLES", "navigate", "go_home"]