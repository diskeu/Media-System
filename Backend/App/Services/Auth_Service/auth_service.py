# AUTHENTICATION - Service

from __future__ import annotations
# ___________type annotations___________
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from Backend.App.Repositories.token_repo import RefreshTokenRepo
from Backend.App.Repositories.base_repo import BaseRepo
from Backend.App.Repositories.user_repo import UserRepo
from typing import Callable, Any, Awaitable
from utils.sentinel import DEFAULT
# ______________Models__________________
from Backend.App.Models.user import User
from Backend.App.Models.refresh_token import RefreshToken
# _____Hashing / (en/de)coding etc._____
from hashlib import sha512
import bcrypt
from base64 import urlsafe_b64encode, urlsafe_b64decode
from hmac import digest as hmac_digest, compare_digest
# _______________Exceptions_____________
from Backend.App.Exceptions.auth_errors import (
    EmailAlreadyExistsError,
    UserNameAlreadyExistsError,
    InvalidPasswordError,
    InvalidEmailError,
    InvalidEmailVerficationTokenError,
    InvalidRefreshTokenError,
    ReplacedRefreshTokenUseError,
    ExpiredRefreshTokenError,
    InvalidUserError,
    InvalidPasswordResetTokenError
)
from Backend.App.Exceptions.service_errors import NotNullError
# ______________________________________
from Backend.App.Services.Auth_Service.verification_mail import build_verification_mail
from email.message import EmailMessage
from datetime import datetime, timedelta
from json import loads as json_loads, dumps as j_dumps, JSONDecodeError
from functools import partial
import random
import string
import re
RepoError = BaseRepo.RepoError

class AuthService():
    """Class for authenticating users"""
    PASSW_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%*!?])[A-Za-z\d@$#%*!?]{8,20}$"
    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    WrapperFunc = Callable[[], EmailMessage]
    SyncDeliverer = Callable[[], EmailMessage | None]
    
    def __init__(
            self,
            user_repo: UserRepo,
            refresh_token_repo: RefreshTokenRepo,
            verification_tokens_c: VerificationTokens,
            password_reset_token_c: VerificationTokens,
            mail_sender: MailSender,
            SECRET: bytes,
            ISSUER: str,
            JWT_EXP_TIME: timedelta,
            SENDER_EMAIL: str,
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
        self.password_reset_token_c: VerificationTokens
        self.refresh_token_repo = refresh_token_repo
        self.mail_sender = mail_sender
        self.SECRET = SECRET
        self.ISSUER = ISSUER
        self.SENDER_EMAIL = SENDER_EMAIL
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
    def __generate_hash(self, password: str) -> str:
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(bytes, salt)
    
    def _generate_refresh_token(self, user_id: int) -> tuple[RefreshToken, str]:
        """
        Generates a 24 digit token and returns (RefreshToken model, token)
        """
        # generating token
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))

        # hashing the token
        token_h = sha512(
            token.encode(), usedforsecurity=True
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

        return (refresh_token_m, token)

    def _generate_jwt(
            self,
            user_id: int,
            user_name: str,
            email: str,
            user_creation: datetime,
            birthdate: datetime
        ):
        header = {
            "alg": "HS256",
            "typ": "jwt"
        }
        payload = {
            "iss": self.ISSUER,
            "sub": user_id,
            "exp": (datetime.now() + self.JWT_EXP_TIME).strftime("%Y-%m-%d %H:%M:%S"), # -> Datetime str
            "iat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": user_name,
            "email": email,
            "user_creation": user_creation,
            "birthdate": birthdate.strftime("%Y-%m-%d")
        }
        # parse the header and payload into json format
        json_dumps = partial(j_dumps, default=str)
        header_json, payload_json = map(json_dumps, (header, payload))

        urlsafe_b64_header = urlsafe_b64encode(header_json.encode())
        urlsafe_b64_payload = urlsafe_b64encode(payload_json.encode())

        data = urlsafe_b64_header + b"." + urlsafe_b64_payload

        sign = hmac_digest(
            key=self.SECRET,
            msg=data,
            digest="sha256"
        )
        jwt = urlsafe_b64_header + b"." + urlsafe_b64_payload + b"." + urlsafe_b64encode(sign)

        # decode jwt & remove trailing '='
        return jwt.decode().rstrip("=")

    def account_verification_mail(
        self,
        user_name: str | None,
        user_email: str | None,
        verification_token: str,
        *,
        sender_email: str | None = None,
        subject: str | None = None,
        template: str | None = None,
        **format_map: Any
        ) -> Callable[[SyncDeliverer], self.WrapperFunc]:
        """
        Decorates a `sync_deliverer` func to just return an appropriate `EmailMessage` designed
        for verification-mails object with the given user_name, user_email and verification_token.
        User_name, user_email & verification_token are only optional if a template is given.

        Raises:
            ValueError
        """
        def decorator(func: self.SyncDeliverer) -> self.WrapperFunc:
            def wrapper() -> Callable[[], EmailMessage]:
                # getting html mail message
                if template:
                    body = template.format_map(
                        {
                            **format_map,
                            **({"user_name": user_name} if user_name else {}),
                            **({"user_email": user_email} if user_email else {}),
                            **({"verification_token": verification_token} if verification_token else {})
                        }
                    )
                else:
                    if None in (user_name, user_email, verification_token):
                        raise ValueError("Error in optional args, Check the docs")
                    body = build_verification_mail(
                        user_name, verification_token
                    )
                # Building msg
                msg = EmailMessage()
                msg.set_content(body, subtype="html")
                msg["SUBJECT"] = "Confirm your Media-System account" if not subject else subject
                msg["FROM"] = sender_email if sender_email else self.SENDER_EMAIL
                msg["TO"] = user_email

                return msg
            return wrapper
        return decorator
    """
    Sends Mail using the defined mail in verification_mail.py and
    returns the google api's json return in dict format
    """
        
    def _validate_jwt(self, jwt: str) -> bool | tuple[dict, dict]:
        """
        Valuates a Json Web Token and returns False | (dict[header], dict[payload])
        """
        def _add_padding(s: str) -> str:
            """
            Adds back in the required padding before decoding.
            """
            padding = -len(s) % 4
            return s + ("=" * padding)
        try:
            header, payload, sign = jwt.split(".")
        except ValueError: return False

        data = header.encode() + b"." + payload.encode()

        expected_sign = urlsafe_b64encode(
                hmac_digest(
                    key=self.SECRET,
                    msg=data,
                    digest="sha256"
            )
        ).decode()
        if not compare_digest(_add_padding(sign), expected_sign):
            return False
        
        # decode json -> python dict
        try:
            header_dict, payload_dict = map(
                json_loads,
                map(
                    urlsafe_b64decode,
                    map(_add_padding, (header, payload))
                )
            )
        except JSONDecodeError as e:
            return False
        
        # format non-serializable json-formats
        try:
            payload_dict["birthdate"] = datetime.strptime(payload_dict["birthdate"], '%Y-%m-%d')
            payload_dict["exp"] = datetime.strptime(payload_dict["exp"], '%Y-%m-%d %H:%M:%S')
            payload_dict["iat"] = datetime.strptime(payload_dict["iat"], '%Y-%m-%d %H:%M:%S')
        except ValueError: return False
        # checking exp time
        if (payload_dict["exp"] - payload_dict["iat"]).total_seconds() <= 0:
            return False
        return (header_dict, payload_dict)
    
    async def login(self, email: str, password: str) -> tuple[str, str] | RepoError:
        """
        Login a user via email & password.
        Returns (refresh_token_hash, jwt).
        Raises
            InvalidPasswordError
            InvalidEmailError
        """
        # validate email & password regex first
        if not self.validate_password(password): raise InvalidPasswordError("Password is incorrect")
        if not self.validate_email(email): raise InvalidEmailError("Email is incorrect")

        return_val = await self.user_repo.check_user(email)
        if isinstance(return_val, RepoError): return return_val

        if not return_val: raise InvalidUserError("Email corresponds to no user")
        return_dict = return_val[0]
        
        if not bcrypt.checkpw(
            password.encode(),
            return_dict["hashed_password"].encode()
        ): raise InvalidPasswordError("Password is incorrect")

        # generating refresh token and jwt
        refresh_token_model, token = self._generate_refresh_token(return_dict["user_id"])
        refresh_token_model.user_id = return_dict["user_id"] # -> update DEFAULT to user_id

        jwt = self._generate_jwt(
            user_id=return_dict["user_id"],
            user_name=return_dict["user_name"],
            email=return_dict["email"],
            user_creation=return_dict["created_at"],
            birthdate=return_dict["birth_date"]
        )
        # insert refresh token into DB
        return_val = await self.refresh_token_repo.insert_token_model(refresh_token_model)
        if isinstance(return_val, RepoError): return return_val

        return (token, jwt)

    async def refresh(self, refresh_token: str, token_rotation: bool = False) -> None | tuple[str, str] | str | RepoError:
        """
        checks the validity of the refresh_token and returns a pair
        of new (refresh_token if token_rotation == True, acces_token) | None if refresh_token is invalid.
        If a invalid refresh_token is used, then all tokens from the client become invalid. the User needs
        to log in again.
        Raises
            InvalidRefreshTokenError,
            ReplacedRefreshTokenUseError,
            ExpiredRefreshTokenError
        """
        token_h = sha512(
            refresh_token.encode(), usedforsecurity=True
        ).digest()

        return_val = await self.refresh_token_repo.validate_token_hashes([token_h])
        if isinstance(return_val, RepoError): return return_val
        
        if not return_val: raise InvalidRefreshTokenError() # -> Token is invalid

        return_dict = return_val[0]
        
        # invalid all client tokens if token is replaced
        if return_dict["outdated_token_use"]:
            print("INVALID ALL REFRESH TOKENS")
            r_v = await self.refresh_token_repo.invalid_all_refresh_tokens(return_dict["user_id"])
            if isinstance(r_v, RepoError): return r_v
            raise ReplacedRefreshTokenUseError()
        if return_dict["expired"]: raise ExpiredRefreshTokenError()

        # get jwt
        jwt = self._generate_jwt(
            user_id=return_dict["user_id"],
            user_name=return_dict["user_name"],
            email=return_dict["email"],
            user_creation=return_dict["created_at"],
            birthdate=return_dict["birth_date"]
        )
        # Token rotation
        if token_rotation:
            new_token_m, token = self._generate_refresh_token(return_dict["user_id"])
            r_v = await self.refresh_token_repo.token_rotation(
                    user_id=return_dict["user_id"],
                    token_id=return_dict["token_id"],
                    new_token_hash=new_token_m.token_hash
                )
            if isinstance(r_v, RepoError): return r_v

            return (jwt, token)
        return jwt

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
            hashed_password=self.__generate_hash(password),
            email=email,
            created_at=DEFAULT,
            birth_date=birth_date,
            last_seen=DEFAULT
        )
                
        # keep all active tokens in-memory
        token = self.verification_tokens_c.generate_token(user)

        # email verification
        @self.mail_sender.send_mail_async(thread_pool=self.thread_pool)
        @self.account_verification_mail(
            user_name=user.user_name,
            user_email=user.email,
            verification_token=token
        )
        def mail_deliverer(): ...
        
        await mail_deliverer()

    async def validate_email_token(self, token: str) -> tuple[str, str] | RepoError:
        """
        Wrapper for verification_tokens.validate_token.
        If the corresponding Token is valid, insert the user into the DB
        and return (refresh_token, jwt)
        Raises:
            InvalidEmailVerficationToken if the token is not valid
        """
        user_m: User = self.verification_tokens_c.validate_token(token)
        if user_m == False: raise InvalidEmailVerficationTokenError

        sucess = await self.user_repo.insert_user(user_m, return_last_insert_id=True)
        
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
            raise sucess
        jwt = self._generate_jwt(
            user_m.user_id,
            user_m.user_name,
            user_m.email,
            user_m.created_at,
            user_m.birth_date
        )
        # generating refresh token and insert it into the DB 
        token_m, token = self._generate_refresh_token(user_m.user_id)

        # updating token_m
        token_m.user_id = sucess
        return_val = await self.refresh_token_repo.insert_token_model(token_m)
        if isinstance(return_val, RepoError): return return_val

        return (token, jwt)
    
    async def request_password_reset(self, user_m: User):
        """
        Sends a password reset link
        Raises
            InvalidEmailError
        """
        if not self.validate_email(user_m.email):
            raise InvalidEmailError

        # storing token
        self.password_reset_token_c.generate_token(
            user_m=user_m
        )
        @self.mail_sender.send_mail_async(thread_pool=self.thread_pool)
        @self.account_verification_mail(
            user_name=None,
            user_email=user_m.email,
            verification_token=None,
            sender_email=None,
            template=body,
            # format map
            token=token_hash
        )
        def password_reset_message(): ...
    
    async def validate_password_reset_token(self, token: str, new_password: str) -> None | RepoError:
        """
        Given a password-reset token & password, validates
        it and changes the password
        """
        if not (user_m := self.password_reset_token_c.validate_token(token)):
            raise InvalidPasswordResetTokenError 

        new_password_hash = self.__generate_hash(new_password)

        return await self.user_repo.update_single_user(
                user_id=user_m.user_id,
                values={"hashed_password": new_password_hash}
            )