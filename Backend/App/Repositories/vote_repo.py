# Repo to access / post data, related to the votes-table
from __future__ import annotations
from Backend.App.Models.vote import Vote
from Backend.App.Repositories.base_repo import BaseRepo

class VoteRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx
    
    def get_users_vote(self, user_id, *post_ids: str) -> dict[int, int] | BaseRepo.RepoError:
        """
        Given a user and posts, returns the status of the users vote in format dict \n
        -> {post_id: -1 | 1} for all values where user has placed a vote or RepoError
        """
        condition = "WHERE user_id = %s AND post_id IN ({})".format(
                ", ".join(
                    "%s" for _ in range(len(post_ids))
                )
            )
        sql_return_val: list = self.get_all(
            "messenger.votes",
            condition,
            (user_id, *post_ids),
            "post_id, vote"
        )
        if isinstance(sql_return_val, self.RepoError): return sql_return_val

        # formatting into {post_id: -1 | 1, ...}
        post_id_to_vote = {post_vote.get("post_id"): post_vote.get("vote") for post_vote in sql_return_val}
        return post_id_to_vote

    def vote(self, user_id, post_id, mode: int) -> None | BaseRepo.RepoError:
        """
        Given an user_id, post_id and mode will do a vote related task depending on the vote\n
        Modes:
            1: 'upvote'
            2: 'downvote'
            3: 'unvote'
        """
        if mode == 3:
            delete_query = self.build_delete_query(
                "messenger.votes",
                "WHERE user_id = %s AND post_id = %s"
            )
            return self.execute_write(delete_query, user_id, post_id) # None | RepoError

        vote_instance = Vote(
            user_id,
            post_id,
            1 if mode == 1 else -1
        )
        # Checking on Repo Error
        columns_values: tuple = self.get_columns_values(vote_instance)
        if isinstance(columns_values, self.RepoError): return columns_values
        columns, values = columns_values

        # delete ';' and adding duplicate key statement
        insert_query, insert_vals = self.build_insert_query("messenger.votes", columns, values)
        insert_query = insert_query[:-1]
        insert_vals.append(vote_instance.vote)
        insert_query += " ON DUPLICATE KEY UPDATE vote = %s;"

        self.execute_write(insert_query, *insert_vals)