# class for verification-tokens
from Backend.App.Models.user import User
from hashlib import sha256
from datetime import datetime
from asyncio import sleep
from random import choice
import hmac
class VerificationTokens():
    """
    Small class that helps keep track of active tokens in-memory,
    generates token and checks if a token is valid
    """
    def __init__(self, token_expiry_time: int):
        self.token_dict = {}
        self.token_expiry_time = token_expiry_time

    async def token_tracker(self, intervall: int):
        """Removes every expired Token in the token_dict"""
        while True:
            await sleep(intervall)
            for k, _, created_at in list(self.token_dict.items()):
                delta = datetime.now() - created_at
                if delta.total_seconds() > self.token_expiry_time:
                    self.token_dict.pop(k)
        
    def generate_token(self, user_m: User) -> str:
        now = datetime.now()
        data = (
            f"{str(now)}"
            f"{user_m.user_name}"
            f"{
                ''.join(
                    random.choices(
                        string.ascii_uppercase + string.digits, k=24
                    )
                )
            }"
            ).encode()

        token_hx = sha256(
            data=data,
            usedforsecurity=True
        ).hexdigest()
        
        self.token_dict[token_hx] = user_m, now
        return token_hx
    
    def validate_token(self, token) -> bool:
        """Checks if token is in the dict -> pops the token if True and returns the User Model"""
        hmac.compare_digest()
        user_m, val = self.token_dict.get(token, (None, None))
        if val:
            self.token_dict.pop(token)
            delta = datetime.now() - val
            if delta.total_seconds() <= self.token_expiry_time:
                return user_m
        return False