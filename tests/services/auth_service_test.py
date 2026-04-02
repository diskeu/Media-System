from Backend.App.Services.Auth_Service.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from Backend.App.Repositories.token_repo import RefreshTokenRepo
from datetime import datetime, timedelta
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
    rt_r = RefreshTokenRepo(
        logger,
        connection
    )
    return connection, u_r, v_t, rt_r

async def connect_test():
    connection, u_r, v_t, _ = await get_auth_service_credentials()
    a_s = AuthService(u_r, v_t, MailSender(0))
    sucess = await a_s.register(
        name="dsadssa",
        email="jelenzt@gmail.com",
        password="0z7ZBu2Bg!J9",
        birth_date=datetime.now(),
    )
    for token in v_t.token_dict: token = token
    print(await a_s.validate_email_token(token))

# asyncio.run(connect_test())

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
    connection, u_r, v_t, rt_r = await get_auth_service_credentials()
    auth_service = AuthService(
        user_repo=u_r,
        refresh_token_repo=rt_r,
        verification_tokens_c=v_t,
        mail_sender=MailSender(0),
        SECRET=b"secret3221",
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
asyncio.run(jwt_test_case())