from Backend.App.Services.Auth_Service.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
from Backend.App.Services.Auth_Service.google_mail_sender import MailSender
from datetime import datetime
import asyncio
import time

async def connect_test():
    connection = await connect(
        "/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root"
    )
    u_r = UserRepo(
        setup_logger(),
        connection
    )
    v_t = VerificationTokens(12)
    a_s = AuthService(u_r, v_t, MailSender(0))
    sucess = await a_s.register(
        name="dsadssa",
        email="jelenzt@gmail.com",
        password="0z7ZBu2Bg!J9",
        birth_date=datetime.now(),
    )
    for token in v_t.token_dict: token = token
    print(await a_s.validate_email_token(token))

asyncio.run(connect_test())

# testing verification_tokens.py
# _______________________________
verification_tokens = VerificationTokens(3) 
# verification_tokens.generate_token()
time.sleep(4)
for token in verification_tokens.token_dict: token = token
# print(verification_tokens.validate_email_token(token))
# asyncio.run(verification_tokens.token_tracker(2))