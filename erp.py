from mockdb import Table as table

payroll = table()
users = table()

def create_account(username: str, password: str, privileges: dict):
    user_id = users.insert({'username': username, 'password': password, 'privileges': privileges})
    return user_id
