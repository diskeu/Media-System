# Community Model for communitys_table
from datetime import datetime
from .base_model import BaseModel
from ....utils.sentinel import DEFAULT

class Community(BaseModel): # TODO -> Change DEFAULT of the community_owner
    def __init__(
        self,
        community_id: int | DEFAULT,
        community_owner: int, # Shouldn't be DEFAULT | None by initialisation, can be DEFAULT later on
        created_at: datetime | DEFAULT,
        community_description: str | DEFAULT | None
    ):
        self.community_id = community_id
        self.community_description = community_description
        self.created_at = created_at
        self.community_owner = community_owner

    def __repr__(self):
        return "<Id {}> <Owner {}>".format(self.community_id, self.community_owner)
        