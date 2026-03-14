# Repo to access / post data, related to the community_members-table
from __future__ import annotations
from Backend.App.Models.community_member import CommunityMember
from Backend.App.Repositories.base_repo import BaseRepo

class CommunityMemberRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    async def get_member_info(self, community_id: int, member_id: int, *columns: str) -> CommunityMember | BaseRepo.RepoError:
        """User - ORM: Given a 'post_id', returns instance of the post class or RepoError"""
        community_model = await self.get_info(
            CommunityMember,
            "messenger.community_members",
            {
                "community_id": community_id,
                "user_id": member_id
            },
            *columns
        )
        
        return community_model # model | RepoError

    async def insert_community_member(self, *models: CommunityMember) -> None | BaseRepo.RepoError:
        """Given CommunityMember models, inserts them into the DB, returns None | RepoError"""
        return await self.post_model(     # None | RepoError
            "messenger.community_members",
            *models
        )

    async def update_community_member_role(self, community_id: int, member_id: int, role: str) -> None | BaseRepo.RepoError:
        """Given a 'member_id', 'community_id', 'role' and a 'mysql.connector.connection_cext.CMySQLConnection', updates the member's values"""
        update_query, insert_values = self.build_update_query(
            table="messenger.community_members",
            update_val={"role": role},
            other_statement="WHERE community_id = %s AND user_id = %s"
        )
        insert_values.extend((community_id, member_id))

        # executing statement
        return await self.execute_write(update_query, *insert_values) # None | RepoError

    async def delete_member(self, community_id: int, *member_ids: int) -> None| BaseRepo.RepoError:
        """Given a list of member_ids, deletes the corresponding members from the community"""
        # making condition
        member_placeholders = ("%s" for _ in range(len(member_ids)))

        # outputs -> WHERE community_id = %s AND member_id IN (%s, %s, %s, %s)
        condition = "WHERE community_id = %s AND user_id IN ({})".format(", ".join(member_placeholders))

        # getting delete query
        delete_query = self.build_delete_query(
            table="messenger.community_members",
            condition=condition
        )

        # executing statement
        return await self.execute_write(delete_query, community_id, *member_ids)