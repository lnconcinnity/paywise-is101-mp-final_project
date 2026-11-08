from app.lib.store import Store

use_store = Store(initial_state={
    "user_accounts": {},
    "current_user": None,
    "pagination": None,
})

use_store.derive("current_role", ["current_user"], lambda user: user.role if user is not None else None)