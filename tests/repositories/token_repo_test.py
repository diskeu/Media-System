from Backend.App.Repositories.token_repo import RefreshTokenRepo
from Backend.App.Models.refresh_token import RefreshToken
from Backend.App.Database.connection import connect
from Backend.App.logger_config import setup_logger
from utils.sentinel import DEFAULT
from hashlib import sha512
import asyncio
import datetime

async def main_test():
    connection = await connect(
        "/Users/TimJelenz/Desktop/messenger/Backend/Configurations/mysql.conf", "root"
    )
    logger = setup_logger()
    refresh_token_r = RefreshTokenRepo(
        logger=logger,
        cnx=connection
    )
    refresh_token_model = RefreshToken(
        token_id=DEFAULT,
        user_id=1002,
        token_hash=sha512("21".encode(), usedforsecurity=True).digest(),
        created_at=DEFAULT,
        t_expiry_date=None, # Trigger
        revoked_at=None,
        replaced_by=None
    )
    # vvvvvvvvvv Test Functions vvvvvvvvvv
    # refresh_token_model.token_id = await refresh_token_r.insert_token_model(refresh_token_model)
    # return_val = await refresh_token_r.validate_token_hashes([refresh_token_model.token_hash, sha512("123212".encode(), usedforsecurity=True).digest()])
    # await refresh_token_r.token_rotation(refresh_token_model, new_token_hash=sha512("31212".encode(), usedforsecurity=True).digest())
    await refresh_token_r.invalid_all_refresh_tokens(1002)

asyncio.run(main_test())
# Test case 1: 1 hash
[
    {
        'token_hash': b'79\xc4WR\xaeq\x0eX8\xb1\xb3\xf6L\xcd\x91\xdf\xa1\xf5j\xbc6Q\xe3\x8d\x83\x99\xd1\xd8\xba\xdc\xc5\x92\xbf\xfb\xe8\x93X\xeb\xba1\xa4\xa6M\xe3\xe1`qf\xe8K$?&}Y\xefa0\x08\xa8yW\x8c',
        'created_at': datetime.datetime(2026, 3, 30, 14, 0, 34),
        'expired': 0,
        'outdated_token_use': 0
    }
]
# Test case 2: 2 hashes
[
    {
        'token_hash': b"\x19\x8d\xab\xf4\xba\xc2\x1c\xf3\\\xdd\xb4\x8d\xb0\xf8\xb6|V\xb2\xbd\xf67g$*\xeasB\xfeh\xc0\xb9\xdf\x8d7\xf3\xe4z\x13FH\xe1\x9f\x16@\xe1X\xf2\xe5'\xe66\xdb\x12*\x91C0|\xf3\t\xef\xcb\x85\xd9",
        'created_at': datetime.datetime(2026, 3, 30, 17, 7, 23),
        'expired': 0,
        'outdated_token_use': 0
    },
    {
        'token_hash': b'79\xc4WR\xaeq\x0eX8\xb1\xb3\xf6L\xcd\x91\xdf\xa1\xf5j\xbc6Q\xe3\x8d\x83\x99\xd1\xd8\xba\xdc\xc5\x92\xbf\xfb\xe8\x93X\xeb\xba1\xa4\xa6M\xe3\xe1`qf\xe8K$?&}Y\xefa0\x08\xa8yW\x8c',
        'created_at': datetime.datetime(2026, 3, 30, 15, 1, 24),
        'expired': 0,
        'outdated_token_use': 0
    }
]
#################################################
# Conclusion: Even if validating 2 (or more)    #
# hashes at the same time is possible, it would #
# lead to confiusion and worse handling. Maybe  #
# add it in the future.                         #
#################################################
