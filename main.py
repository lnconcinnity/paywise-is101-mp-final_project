
from account.Account import Account
from config import *


def run():
    # provision accounts first
    staff = Account("Staff")
    staff.allow(PRIVILEGES["bookkeeping"])

if __name__ == "__main__":
    run()