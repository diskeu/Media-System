from Backend.App.logger_config import setup_logger
from Backend.App.Database.connection import connect
from utils.sentinel import DEFAULT
import asyncio

# testing comment_repo
from Backend.App.Repositories.comment_repo import CommentRepo
from Backend.App.Models.comment import Comment
async def comment_repo():
    connection = await connect("/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root")
    c_r = CommentRepo(setup_logger(), connection)
    x = await c_r.get_comment_info(3)
    print(x.comment_content)

asyncio.run(comment_repo())