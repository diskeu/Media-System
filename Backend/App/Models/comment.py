# comment Model for comments table
from Backend.App.Models.base_model import BaseModel 
from datetime import datetime
from utils.sentinel import DEFAULT

class Comment(BaseModel):
    def __init__(
        self,
        comment_id: int | DEFAULT,
        comment_creator_id: int,
        post_id: int,
        parent_comment_id: int | DEFAULT,
        comment_content: str,
        created_at: datetime | DEFAULT
    ):
        self.comment_id = comment_id
        self.comment_creator_id = comment_creator_id
        self.post_id = post_id
        self.parent_comment_id = parent_comment_id
        self.comment_content = comment_content
        self.created_at = created_at
        
    def __repr__(self):
        return "<Comment Id {}> <Parent Post {}>".format(self.comment_id, self.parent_comment_id)