# AUTHENTICATION - Service

# ___________type annotations___________
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from Backend.App.Repositories.token_repo import RefreshTokenRepo
from Backend.App.Repositories.base_repo import BaseRepo
from Backend.App.Repositories.user_repo import UserRepo
from utils.sentinel import DEFAULT
# ______________________________________
from Backend.App.Models.user import User
from Backend.App.Models.refresh_token import RefreshToken
from hashlib import sha256, sha512
from Backend.App.Exceptions.auth_errors import (
    EmailAlreadyExistsError,
    UserNameAlreadyExistsError,
    InvalidPasswordError,
    InvalidEmailError,
    InvalidEmailVerficationTokenError
)
from Backend.App.Exceptions.service_errors import NotNullError
from datetime import datetime, time
import random
import string
import re
from base64 import urlsafe_b64encode
RepoError = BaseRepo.RepoError

class AuthService():
    """Class for authenticating users"""
    PASSW_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%*!?])[A-Za-z\d@$#%*!?]{8,20}$"
    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    def __init__(
            self,
            user_repo: UserRepo,
            refresh_token_repo: RefreshTokenRepo,
            verification_tokens_c: VerificationTokens,
            mail_sender: MailSender,
            SECRET: str,
            ISSUER: str,
            JWT_EXP_TIME: time,
            thread_pool = None,
        ):
        """
        Param:
            user_repo: UserRepo that should be used
            verification_tokens_c: a VerificationTokens - Class to avoid creating new ones
            mail_sender: MailSender class for sending verification tokens
            thread_pool: If None use the standart ThreadPool
        """
        self.user_repo = user_repo
        self.verification_tokens_c = verification_tokens_c
        self.refresh_token_repo = refresh_token_repo
        self.mail_sender = mail_sender
        self.SECRET = SECRET
        self.ISSUER = ISSUER
        self.JWT_EXP_TIME = JWT_EXP_TIME
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
    
    async def _generate_refresh_token(self, user_id: int) -> bytes:
        """
        Generates a 24 digit token and inserts it's hash into the DB
        """
        # generating token
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))

        # hashing the token
        token_h = sha512(
            token, usedforsecurity=True
        ).digest()

        # defining model
        refresh_token_m = RefreshToken(
            token_id=DEFAULT,
            user_id=user_id,
            token_hash=token_h,
            created_at=DEFAULT,
            t_expiry_date=None, # Trigger
            revoked_at=None,
            replaced_by=None
        )
        self.refresh_token_repo.insert_token_model(refresh_token_m)

        return token_h

    async def _generate_jwt(
            self,
            user_id: int,
            user_name: str,
            email: str,
            user_creation: datetime,
            birthdate: datetime
        ):
        payload = {
            "iss": self.ISSUER,
            "sub": user_id,
            "exp": datetime.combine(datetime.now(), self.JWT_EXP_TIME).timestamp(),
            "iat": datetime.now().timestamp(),
            "user_name": user_name,
            "email": email,
            "user_creation": user_creation,
            "birthdate": birthdate
        }
        header = {
            "alg": "HS256",
            "typ": "jwt"
        }
        data = urlsafe_b64encode(header) + "." + urlsafe_b64encode(payload)
        
    async def refresh(self, refresh_token: bytes) -> bytes: ...

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