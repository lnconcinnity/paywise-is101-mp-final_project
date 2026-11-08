from app.modules.Databases import users_db
from app.modules.Employees import find_employees

STANDARD_HOURS = 8.0
WORK_DAYS = 5
DEFAULT_LEAVE_BALANCE = 12
MAX_DAILY_HOURS = 24.0
NO_LEAVE = "none"

def leave_options() -> tuple[str, ...]:
    return (NO_LEAVE, *(f"Day {i}" for i in range(1, WORK_DAYS + 1)))

def fmt(hours: float) -> str:
    return f"{hours:g}"

def plural(n: float, word: str) -> str:
    return f"{fmt(n)} {word}" if n == 1 else f"{fmt(n)} {word}s"

def parse_hours(raw: str, day: int) -> tuple[float | None, str]:
    if raw == "":
        return 0.0, ""
    try:
        hours = float(raw)
    except ValueError:
        return None, f"Day {day}: hours must be a number."
    if hours < 0:
        return None, f"Day {day}: hours cannot be negative."
    if hours > MAX_DAILY_HOURS:
        return None, f"Day {day}: cannot log more than {MAX_DAILY_HOURS:g} hours."
    return hours, ""

def day_line(day: int, hours: float, on_leave: bool) -> str:
    if on_leave:
        return f"Day {day}: On Leave (Paid)"
    if hours <= 0:
        return f"Day {day}: Absent"
    if hours < STANDARD_HOURS:
        return f"Day {day}: Present ({fmt(hours)} hrs, {fmt(STANDARD_HOURS - hours)} hr undertime)"
    if hours > STANDARD_HOURS:
        return f"Day {day}: Present ({fmt(hours)} hrs, {fmt(hours - STANDARD_HOURS)} hr overtime)"
    return f"Day {day}: Present ({fmt(hours)} hrs)"

def record_week(query: str, raw_hours: list[str], leave: str) -> tuple[bool, list[str]]:
    found = find_employees(query)
    if not found:
        return False, ["No employee found."]
    if len(found) > 1:
        return False, [f"{len(found)} matches. Use the username or ID."]
    record = found[0]
    if record.deactivated:
        return False, [f"{record.name} is deactivated."]

    hours = []
    for i, raw in enumerate(raw_hours, start=1):
        value, error = parse_hours(raw, i)
        if value is None:
            return False, [error]
        hours.append(value)

    leave_day = None if leave == NO_LEAVE else int(leave.split()[1])
    props = record.manifest["properties"]
    balance = props.get("leave_balance", DEFAULT_LEAVE_BALANCE)
    if leave_day is not None:
        if hours[leave_day - 1] > 0:
            return False, [f"Day {leave_day} has hours logged and a leave filed."]
        if balance < 1:
            return False, ["No leave balance left."]
        balance -= 1

    hourly = props["salary"] == "hourly"
    total = sum(hours)
    undertime = sum(max(0.0, STANDARD_HOURS - h) for h in hours if h > 0)
    lines = [f"{record.name} ({'Hourly' if hourly else 'Fixed'})"]
    lines += [day_line(i, h, i == leave_day) for i, h in enumerate(hours, start=1)]
    lines.append(f"Total Hours: {fmt(total)} | Leave Days Used: {0 if leave_day is None else 1}")
    lines.append(f"Leave balance: {plural(balance, 'day')}")
    if hourly and undertime > 0:
        lines.append(f"Undertime deducted: {fmt(undertime)} hr")

    log = [*props.get("attendance", []), {"hours": hours, "leave_day": leave_day}]
    users_db.update(
        record.manifest["id"],
        properties={**props, "leave_balance": balance, "attendance": log},
    )
    return True, lines

__all__ = ["STANDARD_HOURS", "WORK_DAYS", "leave_options", "record_week"]