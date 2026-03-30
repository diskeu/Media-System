# Repo to acces / post data related to the refresh tokens table
from __future__ import annotations
from Backend.App.Models.refresh_token import RefreshToken
from Backend.App.Repositories.base_repo import BaseRepo
from utils.sentinel import DEFAULT
from utils.error_helpers import return_when_error

class RefreshTokenRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx

    async def insert_token_model(self, *models: RefreshToken) -> None | BaseRepo.RepoError:
        return await self.post_model( # -> None | RepoError
            "messenger.refresh_tokens",
            *models
        )
    
    async def validate_token_hashes(self, token_hash: list[bytes]) -> dict[str: list] | BaseRepo.RepoError:
        """Returns {token_hash: expired: bool}"""

        return await self.get_all_enriched(
            table="messenger.refresh_tokens",
            primary_keys=("refresh_token_hash_p", (token_h,) for token_h in token_hash),
            columns=(
                """
                token_hash,
                IF(TIMESTAMPDIFF(MINUTE, NOW(), expires_at) > 0, FALSE, TRUE) AS expired,
                IF(revoked_by_token_id IS NOT NULL, TRUE, FALSE) AS outdated_token_use
                """
            )
        )
    
    async def token_update(self, model: RefreshToken, new_token_hash: bytes) -> bytes:
        """
        Makes new token to replace the old one
        Returns when an error occures
        """
        token_model = RefreshToken(
            token_id=DEFAULT,
            user_id=model.user_id,
            token_hash=new_token_hash,
            expires_at=None, # Trigger
            revoked_at=None,
            replaced_by=None
        )
        ############################################################
        # The New token is inserted first, so when an error in the #
        # updating of the old token occures, there is no reference #
        # to a non-existing attribute.                             #
        ############################################################

        @return_when_error(BaseRepo.RepoError)
        async def insert_token_model():
            return await self.insert_token_model(token_model)

        @return_when_error(BaseRepo.RepoError)
        async def update_old_token():
            update_query, vals = self.build_update_query(
                table="messenger.refresh_tokens",
                update_val={"replaced_by": token_model.token_id, "revoked_at": DEFAULT},
                other_statement=f"WHERE token_id = {token_model.token_id}"
            )
            return await self.execute_write(update_query, *vals)
        
        if await insert_token_model(): return
        if await update_old_token(): return

        # TODO
        # Update the Whole refresh token table
        #   * update the triggers outdated name
        #   * maybe make token_id to be primary and Index on token_hash
        # make revoked at defaults value to be CURRENT_TIMESTAMP()
        # make the table name to a class attribute
        # get the last inserted value