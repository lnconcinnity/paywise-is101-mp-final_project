from account.Security import Security
from util import is_str


class Account:
    _hash: dict[str, 'Account']

    @staticmethod
    def request_account(name):
        # TODO: create a Security.py for logging in
        return Account._hash[name]

    @staticmethod
    def get_account(name):
        return Account._hash[name]

    @staticmethod
    def create_account(name) -> 'Account':
        acc = Account(name)
        Account._hash[name] = acc
        return acc

    @staticmethod
    def delete_account(name):
        del Account._hash[name]

    def __init__(self, name):
        self._name = name
        self._security = Security()
        self._privileges = []

    def has(self, privilege) -> bool:
        return is_str(privilege) and privilege in self._privileges

    def allow(self, privilege):
        assert not self._security.is_passwordless(), f"cannot assign privilege '{privilege}' to a passwordless user"
        assert is_str(privilege), "privilege must be a string"
        self._privileges.append(privilege)

    def deny(self, privilege):
        self._privileges.remove(privilege)