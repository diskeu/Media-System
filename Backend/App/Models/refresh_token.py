# Refresh Token Model for refresh_tokens table
from datetime import datetime, date
from Backend.App.Models.base_model import BaseModel
from utils.sentinel import DEFAULT

class RefreshToken(BaseModel):
    def __init__(self,
        token_id: int | DEFAULT,
        user_id: int,
        token_hash: bytes,
        created_at: datetime | DEFAULT,
        expires_at: datetime | None, # Trigger
        revoked_at: datetime | None,
        replaced_by: int | None
    ):
        self.token_id = token_id
        self.user_id = user_id
        self.token_hash = token_hash
        self.created_at = created_at
        self.expires_at = expires_at
        self.revoked_at = revoked_at
        self.replaced_by = replaced_by
    
    def __repr__(self):
        return f"<ID {self.token_id}> <Expires at {self.expires_at}>"
