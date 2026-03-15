# AUTHENTICATION - Service

from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.Models.user import User
from utils.sentinel import DEFAULT
from hashlib import sha256
from datetime import datetime
class AuthService():
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, name: str, email: str, password: str, birth_date: datetime, rem: bool = False):
        """
        Create a new Account.

        'rem' indicates wheter the cookie should be
        a session (invalid after closing of the browser)
        or persistent (invalid after reaching expiry date)
        cookie.
        """
        print(User.__annotations__)
        user = User(
            user_id=DEFAULT,
            user_name=name,
            hashed_password=sha256(password),
            email=email,
            created_at=DEFAULT,
            birth_date=birth_date,
            last_seen=DEFAULT
        )
        await self.user_repo.insert_user(
            
        )