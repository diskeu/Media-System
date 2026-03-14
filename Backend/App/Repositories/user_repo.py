# repo to acces / post user data to the database
from __future__ import annotations
from Backend.App.Models.user import User
from Backend.App.Repositories.base_repo import BaseRepo

class UserRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    async def get_user_info(self, user_id: int, *columns: str) -> User | BaseRepo.RepoError:
        """User - ORM: Given a 'user_id', returns instance of the user class or RepoError"""
        user_model = await self.get_info(
            User,
            "messenger.users",
            {"user_id": user_id},
            *columns
        )
        return user_model # model | RepoError
    

    async def insert_user(self, *models: User) -> None | BaseRepo.RepoError:
        """Given user models, inserts them into the DB, returns None | RepoError"""
        return await self.post_model(     # None | RepoError
            "messenger.users",
            *models
        )
    
    async def update_single_user(self, user_id, values: dict) -> None | BaseRepo.RepoError:
        """Given a 'user_id', values and a 'mysql.connector.connection_cext.CMySQLConnection', updates the user's values"""
        update_query, insert_values = self.build_update_query(
            table="messenger.users",
            update_val=values,
            other_statement="WHERE user_id = %s"
        )
        insert_values.append(user_id)

        # executing statement
        return await self.execute_write(update_query, *insert_values) # None | RepoError

    async def delete_users(self, *users: int) -> None| BaseRepo.RepoError:
        """Given a list of user_ids, deletes the corresponding users"""
        # making condition
        user_statement = ["%s" for _ in range(len(users))]
        condition = f"WHERE user_id IN ({", ".join(user_statement)})"

        # getting delete query
        delete_query = self.build_delete_query(
            table="messenger.users",
            condition=condition
        )
        # executing statement
        return await self.execute_write(delete_query, *users)