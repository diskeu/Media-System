from Backend.App.Services.Auth_Service.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from Backend.App.Repositories.token_repo import RefreshTokenRepo
from datetime import datetime, timedelta, date
from email.message import EmailMessage
from Backend.App.Models.user import User
import asyncio
import time
async def get_auth_service_credentials():
    logger = setup_logger()
    connection = await connect(
        "/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root"
    )
    u_r = UserRepo(
        logger,
        connection
    )
    v_t = VerificationTokens(12)
    p_r_t = VerificationTokens(4)
    rt_r = RefreshTokenRepo(
        logger,
        connection
    )
    return connection, u_r, v_t, rt_r, p_r_t

async def test_registration():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    a_s = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)

    )
    sucess = await a_s.register(
        name="test_ser",
        email="jelenzt@gmail.com",
        password="0z7ZBu2Bg!J9",
        birth_date=datetime.now(),
    )
    for token in v_t.token_dict: token = token
    print(await a_s.validate_email_token(token))

# asyncio.run(test_registration())

# testing verification_tokens.py
# _______________________________
# verification_tokens = VerificationTokens(3) 
# verification_tokens.generate_token()
# time.sleep(4)
# for token in verification_tokens.token_dict: token = token
# print(verification_tokens.validate_email_token(token))
# asyncio.run(verification_tokens.token_tracker(2))

# Testcase for the '_generate_jwt' and '_validate_jwt' funcs
async def jwt_test_case():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    auth_service = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)
    )

    jwt1 = auth_service._generate_jwt(32, "something", "something@email", datetime.now(), birthdate=datetime.now())
    jwt2 = auth_service._generate_jwt(2122, "something", "something@email", datetime.now(), birthdate=datetime.now())
    jwt3 = auth_service._generate_jwt(2332, "something", "something@email", datetime.now(), birthdate=datetime.now())
    # print("JWT1", jwt1)
    # print("JWT2", jwt2)
    # print("JWT3", jwt3)

    print(auth_service._validate_jwt(jwt1))
    print(auth_service._validate_jwt(jwt2))
    print(auth_service._validate_jwt(jwt3))
    print(auth_service._validate_jwt("wrong-jwt.s"))
# asyncio.run(jwt_test_case())

# Testcase for refresh func
async def refresh_test_case():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    auth_service = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)
    )
    refresh_token = "0K3UGZF8V0127DJ50HH7JD1U" # -> Valid refresh Token
    print(await auth_service.refresh(refresh_token=refresh_token, token_rotation=True))
    print(await auth_service.refresh(refresh_token=refresh_token))

# asyncio.run(refresh_test_case())

# Testcase for the login func
async def login_test_case():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    auth_service = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)
    )
    print(await auth_service.login("jelenzt@gmail.com", "0z7ZBu2Bg!J9"))

# asyncio.run(login_test_case())

# Testcase for mail sending
async def mail_send_test_case():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    a_s = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)

    )
    @a_s.mail_sender.send_mail_async()
    def mail_deliverer(name: str, line_end: str = "."):
        body = f"<h1>hello {name}{line_end}</h1>"
        msg = EmailMessage()
        msg.set_content(body, subtype="html")
        msg["SUBJECT"] = "Confirm your Media-System account"
        msg["FROM"] = "marvinmagmud@gmail.com"
        msg["TO"] = "jelenzt@gmail.com"
        return msg
    await mail_deliverer("Tim")

# asyncio.run(mail_send_test_case())

# Testcase for requesting a password reset
async def request_password_reset():
    connection, u_r, v_t, rt_r, p_r_t = await get_auth_service_credentials()
    a_s = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        password_reset_token_c=p_r_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
        SENDER_EMAIL="marvinmagmud@gmail.com",
        ISSUER="something",
        JWT_EXP_TIME=timedelta(hours=2)
    )
    user_m = User(
        user_id=12,
        user_name="abc",
        hashed_password="123",
        email="jelenzt@gmail.com",
        birth_date=date(1990, 1, 1),
        created_at=datetime.now(),
        last_seen=None

    )
    await a_s.request_password_reset(user_m)
    for token in p_r_t.token_dict: token = token
    print(await a_s.validate_password_reset_token(token=token, new_password="new_password"))

# asyncio.run(request_password_reset())