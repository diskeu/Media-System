from Backend.App.Services.auth_service import AuthService
from Backend.App.Repositories.user_repo import UserRepo
from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
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

asyncio.run(connect_test())