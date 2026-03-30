# AUTHENTICATION - Service

# ___________type annotations___________
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from Backend.App.Repositories.base_repo import BaseRepo
from Backend.App.Repositories.user_repo import UserRepo
from utils.sentinel import DEFAULT
from datetime import datetime
# ______________________________________
from Backend.App.Models.user import User
from hashlib import sha256, sha512
from Backend.App.Exceptions.auth_errors import (
    EmailAlreadyExistsError,
    UserNameAlreadyExistsError,
    InvalidPasswordError,
    InvalidEmailError,
    InvalidEmailVerficationTokenError
)
from Backend.App.Exceptions.service_errors import NotNullError
import random
import string
import re
RepoError = BaseRepo.RepoError

class AuthService():
    """Class for authenticating users"""
    PASSW_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%*!?])[A-Za-z\d@$#%*!?]{8,20}$"
    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    def __init__(self, user_repo: UserRepo, verification_tokens_c: VerificationTokens, mail_sender: MailSender, thread_pool = None):
        """
        Param:
            user_repo: UserRepo that should be used
            verification_tokens_c: a VerificationTokens - Class to avoid creating new ones
            mail_sender: MailSender class for sending verification tokens
            thread_pool: If None use the standart ThreadPool
        """
        self.user_repo = user_repo
        self.verification_tokens_c = verification_tokens_c
        self.mail_sender = mail_sender
        self.thread_pool = thread_pool

    def validate_password(self, password: str) -> bool:
        flag = re.search(AuthService.PASSW_REGEX, password)
        if isinstance(flag, re.Match) == False:
            return False
        return True
    
    def validate_email(self, email: str) -> bool:
        flag = re.search(AuthService.EMAIL_REGEX, email)
        if isinstance(flag, re.Match) == False:
            return False
        return True
    
    async def _generate_refresh_token(self,) -> str:
        """
        Generates a 24 digit token and inserts it's hash into the DB
        """
        # generating token
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))

        # hashing the token
        token_h = sha512(
            token, usedforsecurity=True
        ).digest()

        # TODO: insert the hash into the DB

        # ...

        return token

    async def register(self, name: str, email: str, password: str, birth_date: datetime):
        """
        Create a new Account.

        Raises: (
            InvalidPasswordError,
            InvalidEmailError, 
            EmailAlreadyExistsError, 
            UserNameAlreadyExistsError,
            NotNullError,
            RepoError
        )
        """
        # Validation-code should be sent via javascript
        # Validation in Backend is still necessary
        p_flag = self.validate_password(password)
        if p_flag != True: raise InvalidPasswordError() 

        e_flag = self.validate_email(email)
        if e_flag != True: raise InvalidEmailError()
        
        user = User(
            user_id=DEFAULT,
            user_name=name,
            hashed_password=sha256(password.encode()).hexdigest(),
            email=email,
            created_at=DEFAULT,
            birth_date=birth_date,
            last_seen=DEFAULT
        )
                
        # email verification
        # keep all active tokens in-memory
        token = self.verification_tokens_c.generate_token(user)
        await self.mail_sender.send_mail_async(
            user.user_name,
            user.email,
            verification_token=token,
            thread_pool=self.thread_pool
        )

    async def validate_email_token(self, token: str):
        """
        Wrapper for verification_tokens.validate_token.
        If the corresponding Token is valid, insert it into the DB.
        Raises:
            InvalidEmailVerficationToken if the token is not valid
        """
        user_m = self.verification_tokens_c.validate_token(token)
        if user_m == False: raise InvalidEmailVerficationTokenError

        sucess = await self.user_repo.insert_user(user_m)
        
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