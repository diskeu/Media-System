# AUTHENTICATION - Service

from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.Models.user import User
from Backend.App.Repositories.base_repo import BaseRepo
from utils.sentinel import DEFAULT
from hashlib import sha256
from datetime import datetime
from Backend.App.Exceptions.auth_errors import (
    EmailAlreadyExistsError,
    UserNameAlreadyExistsError,
    InvalidPasswordError,
    InvalidEmailError
)
from Backend.App.Exceptions.service_errors import NotNullError
import re
RepoError = BaseRepo.RepoError

class AuthService():
    PASSW_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%*])[A-Za-z\d@$#%]{8, 20}$"
    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def validate_password(self, password: str) -> bool:
        if re.search(AuthService.PASSW_REGEX, password) == None:
            return False
        return True
    
    def validate_email(self, email: str) -> bool:
        if re.search(AuthService.EMAIL_REGEX, email) == None:
            return False
        return True

    async def register(self, name: str, email: str, password: str, birth_date: datetime, rem: bool = False):
        """
        Create a new Account.

        'rem' indicates wheter the cookie should be
        a session (invalid after closing of the browser)
        or persistent (invalid after reaching expiry date)
        cookie.
        """
        user = User(
            user_id=DEFAULT,
            user_name=name,
            hashed_password=sha256(password.encode()).hexdigest(),
            email=email,
            created_at=DEFAULT,
            birth_date=None,
            last_seen=DEFAULT
        )
        if self.validate_password(password) == False:
            raise InvalidPasswordError() 
        
        if self.validate_email(email) == False:
            raise InvalidEmailError()
        
        sucess = await self.user_repo.insert_user(user)
        
        if isinstance(sucess, RepoError):
            msg = str(sucess.exception)
            
            # Existing Attribute Error
            if sucess.error_code == 8:
                if "email" in msg:
                    raise EmailAlreadyExistsError()
                elif "user_name" in msg:
                    raise UserNameAlreadyExistsError()
                elif "cannot be null" in msg:
                    raise NotNullError()
                else:
                    raise RepoError.error_table[8](msg)