class Security:
    def __init__(self):
        self._password = None
        self.attempts = 0

    def is_passwordless(self) -> bool:
        return self._password is None

    def set(self, new_password: str):
        assert len(new_password) >= 6, "new_password must be 6 characters or more"
        self._password = new_password

    def against(self, password: str) -> bool:
        if self.is_passwordless(): return True
        if password == self._password:
            return True
        self.attempts += 1
        return False