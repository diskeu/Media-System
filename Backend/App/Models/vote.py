# Vote Model for votes table
from .base_model import BaseModel

class Vote(BaseModel):
    def __init__(
        self,
        user_id: int,
        post_id: int,
        vote: int
    ):
        self.user_id = user_id
        self.post_id = post_id
        self.vote = vote
    
    def __repr__(self):
        return "<User Id {}> <Post Id {}".format(self.user_id, self.post_id)
        