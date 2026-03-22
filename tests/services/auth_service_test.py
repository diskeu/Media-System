from Backend.App.Services.Auth_Service.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from Backend.App.Services.Auth_Service.verification_tokens import VerificationTokens
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
    a_s = AuthService(u_r)
    sucess = await a_s.register(
        name="dsadssa",
        email="jelenzt@gmail.com",
        password="0z7ZBu2Bg!J9",
        birth_date=datetime.now(),
    )

# asyncio.run(connect_test())

# testing verification_tokens.py
verification_tokens = VerificationTokens(3) 
verification_tokens.generate_token("marvin")
time.sleep(4)
for token in verification_tokens.token_dict: token = token
print(verification_tokens.validate_token(token))
asyncio.run(verification_tokens.token_tracker(2))