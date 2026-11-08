from app.modules.GlobalStore import use_store
from app.modules.UserRecord import UserRecord

user_records = [
    UserRecord.create("Gian Dwayne", "Romero", "gianromero", "hr_manager"),
    UserRecord.create("Aroll Anne", "Guiang", "arollguiang", "payroll_manager")
]

use_store.set("user_accounts", {
    user.username: { 
        "account": user, 
        "security": { "login_attempts": 0, "locked": False }
    } for user in user_records
})
