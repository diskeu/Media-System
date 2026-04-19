from ...Backend.App.Database.connection import connect 
import asyncio
async def foo():
    cnx = await connect("/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root")
    async with await cnx.cursor() as cursor:
        await cursor.execute("SELECT * FROM messenger.users WHERE user_id = 1002")
        result = await cursor.fetchall()
        print(result)

asyncio.run(foo())
