from mockdb import Table as table
from typing import Literal

type EmployeeCategory = Literal['Regular', 'Contractual', 'Probationary']
type EmployeeSalaryType = Literal['Hourly', 'Fixed']
type EmployeeStatus = Literal['Active', 'Resigned', 'Terminated']

users = table("username")
records = table("name")

def create_account(
    username: str,
    password: str,
    privileges: dict
) -> int:
    user_id = users.insert({
        'username': username,
        'password': password,
        'privileges': privileges
    })
    return user_id

def create_record_for(
    name: str,
    category: EmployeeCategory,
    salary_type: EmployeeSalaryType,
    department_name: str="Unavailable",
    position_name: str | None = None,
) -> int:
    record_id = records.insert({
        'name': name,
        'category': category,
        'salary_type': salary_type,
        'role': { 'department': department_name, 'position': position_name },
        'status': "Active"
    })

def update_record_of(
    name: str,
    **changes,
):
    record_id = records.find(name)
    records.update(record_id, **changes)