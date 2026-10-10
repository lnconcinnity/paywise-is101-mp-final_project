from erp import create_account
from terminal import Scheduler
from app import layout

if __name__ == "__main__":
    # Create three sample accounts with verbose enterprise permissions
    create_account(
        "Jane Doe",
        "password123",
        {
            "role": "payroll_manager",
            "permissions": [
                "view_salary",
                "edit_salary",
                "view_payroll",
                "approve_payroll",
                "create_draft",
                "edit_draft",
                "export_summary",
                "export_bank_file",
                "approve_timesheet"
            ]
        }
    )

    create_account(
        "John Smith",
        "securepass456",
        {
            "role": "hr_manager",
            "permissions": [
                "view_public_profile",
                "view_sensitive_profile",
                "create_employee",
                "edit_employee_profile",
                "approve_pto",
                "manage_users"
            ]
        }
    )

    create_account(
        "Alice Johnson",
        "mypassword789",
        {
            "role": "employee",
            "permissions": [
                "view_public_profile",
                "view_timesheet",
                "request_pto",
                "view_payslip"
            ]
        }
    )

    # Initialize the UI layout
    content = layout()
    Scheduler.populate(content)

    # Start the application
    Scheduler.run()