from app.modules.Databases import users_db
from app.lib.security import verify_password

class UserRecord:
    def __init__(self, row_id: int):
        self._row_id = row_id

    @classmethod
    def create(cls, first_name: str, last_name: str, password: str | None=None, role: str = "employee", department: str = "sales", category: str = "regular", salary: str = "hourly", salary_rate: float = 0.0) -> "UserRecord":
        if password is not None: assert len(password) >= 3, "Password must be at least 3 characters long."
        base_dict = {
            "username": f"{first_name.lower().strip()}.{last_name.lower()}",
            "password": password,
            "role": role,
            "properties": {
                "deactivated": False,
                "firstname": first_name,
                "lastname": last_name,
                "department": department,
                "category": category, # regular, contractual, probationary
                "salary": salary, # hourly, fixed
                "salary_rate": salary_rate,
            }
        }

        row_id = users_db.insert(base_dict)
        users_db.update(row_id, id=row_id)
        
        return cls(row_id)

    @property
    def manifest(self) -> dict:
        return users_db.rows[self._row_id]

    @property
    def username(self) -> str:
        return self.manifest["username"]

    @username.setter
    def username(self, new_username: str):
        users_db.update(self._row_id, username=new_username)

    @property
    def role(self) -> str:
        return self.manifest["role"]

    @role.setter
    def role(self, new_role: str):
        users_db.update(self._row_id, role=new_role)

    @property
    def name(self) -> str:
        properties = self.manifest['properties']
        return f"{properties['firstname']} {properties['lastname']}"

    @property
    def deactivated(self) -> bool:
        return self.manifest["properties"]["deactivated"]

    @property
    def passwordless(self) -> bool:
        password = self.manifest["password"]
        return password is None or password == ""
    
    def deactivate(self):
        users_db.update(self._row_id, properties={**self.manifest["properties"], "deactivated": True})

    def authenticate(self, password: str) -> bool:
        if self.passwordless:
            return password == ""
        return verify_password(provided_password=password, stored_password=self.manifest["password"])