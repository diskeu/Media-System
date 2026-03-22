# class for verification-tokens
from hashlib import sha256
from datetime import datetime
from asyncio import sleep
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
            for k, created_at in list(self.token_dict.items()):
                delta = datetime.now() - created_at
                if delta.total_seconds() > self.token_expiry_time:
                    self.token_dict.pop(k)
        
    def generate_token(self, user_name: str) -> str:
        now = datetime.now()
        data = (str(now) + user_name).encode()

        token = sha256(
            data=data,
            usedforsecurity=True
        )
        self.token_dict[token.hexdigest()] = now
    
    def validate_token(self, token) -> bool:
        """Checks if token is in the dict -> pops the token if True"""
        val: datetime = self.token_dict.get(token, None)
        if val:
            self.token_dict.pop(token)
            delta = datetime.now() - val
            if delta.total_seconds() <= self.token_expiry_time:
                return True
        return False