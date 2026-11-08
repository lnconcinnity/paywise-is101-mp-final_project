from terminal import *
from app.components.FormPanel import FormPanel, Text, Choice
from app.modules.Attendance import WORK_DAYS, leave_options, record_week
from app.components.Navigation import go_home

def TimeTrackingPage() -> Page:
    title = TextLabel("PayWise - Attendance & Time Tracking", style=(BOLD, UNDERLINE, BRIGHT_BLUE))

    def submit(v: dict) -> tuple[bool, list[str]]:
        days = [v[f"day{i}"] for i in range(1, WORK_DAYS + 1)]
        return record_week(v["employee"], days, v["leave"])

    form = FormPanel(
        "Weekly Attendance",
        [
            Text("employee", "Employee", width=14),
            *(Text(f"day{i}", f"Day {i}", width=14) for i in range(1, WORK_DAYS + 1)),
            Choice("leave", "Paid leave", leave_options()),
        ],
        "Record Week",
        submit,
        go_home,
        width=42,
        rows=WORK_DAYS + 4,
        side=True,
    )

    stack = StackLayout(
        title,
        form,
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )
    return Page(stack, name="time_tracking", onEnter=form.open, onExit=form.close)

__all__ = ["TimeTrackingPage"]