# post Model for posts Table
from datetime import datetime
from .base_model import BaseModel
from ....utils.sentinel import DEFAULT

class Post(BaseModel):
    def __init__(
        self,
        post_id: int | DEFAULT,
        post_creator: int,
        community_id: int | DEFAULT | None,
        post_title: str | DEFAULT | None,
        post_content: str,
        post_score: int | DEFAULT,
        is_sticky: bool | DEFAULT, # TODO: add migration so is_sticky is a bool
        created_at: datetime | DEFAULT
    ):
        self.post_id = post_id
        self.post_creator = post_creator
        self.community_id = community_id
        self.post_title = post_title
        self.post_content = post_content
        self.post_score = post_score
        self.is_sticky = is_sticky
        self.created_at = created_at

    def __repr__(self):
        return "<Post Id {}> <Creator Id {}".format(self.post_id, self.post_creator)