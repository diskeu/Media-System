# Repo to access / post data, related to the posts-table
from __future__ import annotations
from Backend.App.Models.post import Post
from Backend.App.Repositories.base_repo import BaseRepo

class PostRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    def get_post_info(self, post_id: int, *columns: str) -> Post | BaseRepo.RepoError:
        """User - ORM: Given a 'post_id', returns instance of the post class or RepoError"""
        post_model = self.get_info(
            Post,
            "messenger.posts",
            {"post_id": post_id},
            *columns
        )
        return post_model # model | RepoError

    def insert_post(self, *models: Post) -> None | BaseRepo.RepoError:
        """Given post models, inserts them into the DB, returns None | RepoError"""
        return self.post_model(     # None | RepoError
            "messenger.posts",
            *models
        )

    def update_single_post(self, post_id, values: dict) -> None | BaseRepo.RepoError:
        """Given a 'post_id', values and a 'mysql.connector.connection_cext.CMySQLConnection', updates the post's values"""
        update_query, insert_values = self.build_update_query(
            table="messenger.posts",
            update_val=values,
            other_statement="WHERE post_id = %s"
        )
        insert_values.append(post_id)

        # executing statement
        return self.execute_write(update_query, *insert_values) # None | RepoError

    def delete_posts(self, *posts: int) -> None| BaseRepo.RepoError:
        """Given a list of post_ids, deletes the corresponding posts"""
        # making condition
        post_statement = ["%s" for _ in range(len(posts))]
        condition = f"WHERE post_id IN ({", ".join(post_statement)})"

        # getting delete query
        delete_query = self.build_delete_query(
            table="messenger.posts",
            condition=condition
        )
        # executing statement
        return self.execute_write(delete_query, *posts)
    
    def get_post_hotness_intervall(self, post_hotness):
        hotness_formular = ""
        self.get_all(
            "messenger.posts",
            "WHERE (WHERE NOW() - created_at) <= INTERVAL 48 HOUR",
            hotness_formular)