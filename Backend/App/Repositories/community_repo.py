# Repo to acces / post data related to the community table
from __future__ import annotations
from Backend.App.Models.community import Community
from Backend.App.Repositories.base_repo import BaseRepo

class CommunityRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    async def get_community_info(self, community_id: int, *columns: str) -> Community | BaseRepo.RepoError:
        """Community - ORM: Given a 'community_id', returns instance of the Community class or RepoError"""
        community_model = await self.get_info(
            Community,
            "messenger.communitys",
            {"community_id": community_id},
            *columns
        )
        return community_model # model | RepoError

    async def insert_community(self, *models: Community) -> None | BaseRepo.RepoError:
        """Given Community models, inserts them into the DB, returns None | RepoError"""
        return await self.post_model(     # None | RepoError
            "messenger.communitys",
            *models
        )

    async def update_single_community(self, community_id, values: dict) -> None | BaseRepo.RepoError:
        """Given a 'community_id', values and a 'mysql.connector.connection_cext.CMySQLConnection', updates the community's values"""
        update_query, insert_values = self.build_update_query(
            table="messenger.communitys",
            update_val=values,
            other_statement="WHERE community_id = %s"
        )
        insert_values.append(community_id)

        # executing statement
        return await self.execute_write(update_query, *insert_values) # None | RepoError

    async def delete_communitys(self, *community_id: int) -> None| BaseRepo.RepoError:
        """Given a list of community_id, deletes the corresponding community"""
        # making condition
        statement = ["%s" for _ in range(len(community_id))]
        condition = f"WHERE community_id IN ({", ".join(statement)})"

        # getting delete query
        delete_query = self.build_delete_query(
            table="messenger.community",
            condition=condition
        )
        # executing statement
        return await self.execute_write(delete_query, *community_id)
    