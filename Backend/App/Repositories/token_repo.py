# Repo to acces / post data related to the refresh tokens table
from __future__ import annotations
from Backend.App.Models.refresh_token import RefreshToken
from Backend.App.Repositories.base_repo import BaseRepo
from utils.sentinel import DEFAULT
from datetime import datetime

class RefreshTokenRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    async def insert_token_model(self, *models: RefreshToken) -> int | BaseRepo.RepoError:
        """
        Inserts mostly happen when the client needs a new acces token
        and the server gives back new Acces Token & new Refresh Token
        because the refresh token is outdated.

        Returns the LAST_INSERT_ID | RepoError
        """
        return await self.post_model( # -> None | RepoError
            "messenger.refresh_tokens",
            *models,

            return_last_inserted_id=True
        )
    
    async def validate_token_hashes(self, token_hash: list[bytes]) -> list[dict] | BaseRepo.RepoError:
        """
        Returns
        [{token_h1:, created_at:, token_id:, expired:, outdated_token_use:}, {...}]
        """

        # If the refresh token is invalid,
        # the client should get a 403 status code,
        # with an login again page
        return await self.get_all_enriched(
            table="messenger.refresh_tokens r",
            primary_keys=("token_hash", [(token_h,) for token_h in token_hash]),
            columns=(
                "r.token_hash",
                "r.token_id",
                "u.user_id",
                "u.user_name",
                "u.created_at",
                "u.birth_date",
                "u.email",
                "r.created_at",
                "IF(TIMESTAMPDIFF(MINUTE, NOW(), t_expiry_date) > 0, FALSE, TRUE) AS expired",
                "IF(replaced_by IS NOT NULL, TRUE, FALSE) AS outdated_token_use"
            ),
            joins=[("INNER JOIN messenger.users u ", "u.user_id = r.user_id")]
        )
    async def invalid_all_refresh_tokens(self, user_id: int) -> None | BaseRepo.RepoError:
        """
        Invalidates all refresh tokens from a client.
        Client needs to log in again
        """
        delete_query = self.build_delete_query(
            "messenger.refresh_tokens",
            "WHERE user_id = %s"
        )
        return await self.execute_write(delete_query, user_id)
    
    async def token_rotation(self, user_id: int, token_id: int, new_token_hash: bytes) -> None | BaseRepo.RepoError:
        """
        Makes new token to replace the old one.
        Returns when an error occures
        """
        if isinstance(token_id, DEFAULT):
            self.logger.exception(
                "token_id must be replaced by the actual token_id"
            )
            return self.RepoError(
                succes=False,
                error_code=9,
                message="token_id cannot be DEFAULT",
                exception=TypeError
            )
        # Building new token model
        token_model = RefreshToken(
            token_id=DEFAULT,
            user_id=user_id,
            token_hash=new_token_hash,
            created_at=DEFAULT,
            t_expiry_date=None, # Trigger
            revoked_at=None,
            replaced_by=None
        )
        ############################################################
        # The New token is inserted first, so when an error in the #
        # updating of the old token occures, there is no reference #
        # to a non-existing attribute.                             #
        ############################################################
        
        # call func to post the new token
        return_val = await self.insert_token_model(token_model)
        if isinstance(return_val, self.RepoError): return return_val

        # return val is last_insert_id
        # call func to update the old token
        update_query, vals = self.build_update_query(
                table="messenger.refresh_tokens",
                update_val={
                    "replaced_by": return_val,  # id of the new token
                    "revoked_at": datetime.now()
                },
                other_statement=f"WHERE token_id = {token_id}"
            )
        return await self.execute_write(update_query, *vals)