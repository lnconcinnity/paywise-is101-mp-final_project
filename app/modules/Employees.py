from app.modules.Databases import users_db
from app.modules.GlobalStore import use_store
from app.modules.UserRecord import UserRecord

CATEGORIES = ("regular", "contractual", "probationary")
SALARY_TYPES = ("hourly", "fixed")
STATUSES = ("active", "deactivated")

def register(record: UserRecord) -> None:
    accounts = use_store.get("user_accounts") or {}
    entry = {"account": record, "security": {"locked": False, "login_attempts": 0}}
    use_store.set("user_accounts", {**accounts, record.username: entry})

def add_employee(first: str, last: str, department: str, category: str, salary: str, rate: str) -> tuple[UserRecord | None, str]:
    if not first or not last:
        return None, "First and last name are required."
    if not department:
        return None, "Department is required."
    try:
        amount = float(rate)
    except ValueError:
        return None, "Rate must be a number."
    if amount < 0:
        return None, "Rate cannot be negative."
    username = f"{first.lower()}.{last.lower()}"
    if users_db.has(username):
        return None, f"{username} already exists."
    record = UserRecord.create(
        first, last, None, role="employee",
        department=department, category=category, salary=salary, salary_rate=amount,
    )
    register(record)
    return record, ""

def find_employees(query: str) -> list[UserRecord]:
    q = query.strip().lower()
    if not q:
        return []
    if users_db.has(q):
        return [UserRecord(users_db.find(q))]

    def matches(row: dict) -> bool:
        p = row["properties"]
        first, last = p["firstname"].lower(), p["lastname"].lower()
        return q in (first, last, f"{first} {last}")

    return [UserRecord(row["id"]) for row in users_db.select(where=matches, order_by="username")]

def search_employees(department: str, category: str, status: str) -> list[UserRecord]:
    dept = department.strip().lower()

    def matches(row: dict) -> bool:
        p = row["properties"]
        return (
            (not dept or p["department"].lower() == dept)
            and (category == "any" or p["category"] == category)
            and (status == "any" or p["deactivated"] == (status == "deactivated"))
        )

    return [UserRecord(row["id"]) for row in users_db.select(where=matches, order_by="username")]

def deactivate_employee(query: str) -> tuple[bool, str]:
    found = find_employees(query)
    if not found:
        return False, "No employee found."
    if len(found) > 1:
        return False, f"{len(found)} matches. Use the username."
    record = found[0]
    acting = use_store.get("current_user")
    if acting is not None and acting.username == record.username:
        return False, "You cannot deactivate yourself."
    if record.deactivated:
        return False, f"{record.name} is already deactivated."
    record.deactivate()
    return True, f"Deactivated {record.name}."

def summary(record: UserRecord) -> str:
    p = record.manifest["properties"]
    state = "off" if p["deactivated"] else "on"
    return f"{record.username:<18}{p['department']:<10}{p['category']:<12}{state}"

def profile(record: UserRecord) -> list[str]:
    p = record.manifest["properties"]
    return [
        f"Name: {record.name}",
        f"Username: {record.username}",
        f"Role: {record.role}",
        f"Department: {p['department']}",
        f"Category: {p['category']}",
        f"Pay: {p['salary']} {p['salary_rate']:,.2f}",
        f"Status: {'Deactivated' if p['deactivated'] else 'Active'}",
    ]

__all__ = ["CATEGORIES", "SALARY_TYPES", "STATUSES", "register", "add_employee", "find_employees", "search_employees", "deactivate_employee", "summary", "profile"]