from typing import Callable
from app.components.FormPanel import FormPanel, Text, Choice, Result
from app.modules.Employees import (
    CATEGORIES, SALARY_TYPES, STATUSES, add_employee, find_employees,
    search_employees, deactivate_employee, summary, profile,
)
from terminal.colors import BRIGHT_RED, BRIGHT_YELLOW

RESULT_ROWS = 8

def listing(found: list) -> Result:
    if not found:
        return False, ["No employee found."]
    if len(found) == 1:
        return True, profile(found[0])
    shown = RESULT_ROWS - 1
    lines = [f"{len(found)} found"] + [summary(r) for r in found[:shown]]
    if len(found) > shown:
        lines[-1] = f"+{len(found) - shown + 1} more, narrow the search."
    return True, lines

def add_form(on_back: Callable[[], None]) -> FormPanel:
    def submit(v: dict) -> Result:
        record, error = add_employee(
            v["first"].replace(" ", "_"), v["last"], v["department"].lower(),
            v["category"], v["salary"], v["rate"],
        )
        return (True, [f"Created {record.username}."]) if record else (False, [error])

    return FormPanel(
        "Add New Employee",
        [
            Text("first", "First name",),
            Text("last", "Last name"),
            Text("department", "Department", default="Sales"),
            Choice("category", "Category", CATEGORIES),
            Choice("salary", "Pay type", SALARY_TYPES),
            Text("rate", "Rate", default="0"),
        ],
        "Create Employee", submit, on_back, rows=RESULT_ROWS,
        style=(BRIGHT_YELLOW,)
    )

def view_form(on_back: Callable[[], None]) -> FormPanel:
    return FormPanel(
        "View Employee",
        [Text("query", "Name / username")],
        "Look up",
        lambda v: listing(find_employees(v["query"])),
        on_back, rows=RESULT_ROWS, keep_on_success=True,
        style=(BRIGHT_YELLOW,)
    )

def search_form(on_back: Callable[[], None]) -> FormPanel:
    return FormPanel(
        "Search Filter",
        [
            Text("department", "Department"),
            Choice("category", "Category", ("any", *CATEGORIES)),
            Choice("status", "Status", ("any", *STATUSES)),
        ],
        "Search",
        lambda v: listing(search_employees(v["department"], v["category"], v["status"])),
        on_back, rows=RESULT_ROWS, keep_on_success=True,
        style=(BRIGHT_YELLOW,)
    )

def deactivate_form(on_back: Callable[[], None]) -> FormPanel:
    def submit(v: dict) -> Result:
        ok, message = deactivate_employee(v["query"])
        return ok, [message]

    return FormPanel(
        "Deactivate Employee",
        [Text("query", "Username")],
        "Deactivate", submit, on_back, rows=RESULT_ROWS,
        style=(BRIGHT_RED,)
    )

__all__ = ["add_form", "view_form", "search_form", "deactivate_form"]