from Backend.App.Services.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from datetime import datetime
import asyncio

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
        email="dsa",
        password="dsadasd",
        birth_date=datetime.now(),
    )

asyncio.run(connect_test())