# Community Members Model for community_members table
from datetime import datetime
from .base_model import BaseModel
from ....utils.sentinel import DEFAULT

class CommunityMember(BaseModel):
    def __init__(
        self,
        community_id: int,
        user_id: int,
        role: str | DEFAULT,
        member_since: datetime | DEFAULT,
    ):
        self.community_id = community_id
        self.user_id = user_id
        self.role = role
        self.member_since = member_since

    def __repr__(self):
        return "<Community Id {}> <User Id {}>".format(self.community_id, self.user_id)
    