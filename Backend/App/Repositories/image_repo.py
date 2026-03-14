# Repo to access / post data, related to the images-table
from __future__ import annotations
from Backend.App.Repositories.base_repo import BaseRepo
from Backend.App.Models.vote import Vote

class ImageRepo(BaseRepo):
    def __init__(self, logger, cnx):
        super().__init__(logger)
        self.logger = logger
        self.cnx = cnx
    
    def add_images_to_post(self, *models: Vote) -> None | BaseRepo.RepoError:
        return self.post_model(     # None | RepoError
            "messenger.images",
            *models
        )
    def get_images_path(self, image_ids: list[int] | None, post_ids: list[int] | None) -> list[dict[any]] | BaseRepo.RepoError:
        """
        Gets all paths of the images of the specific image_ids\n
        Pare image_ids or post_ids not both
        """
        if image_ids and post_ids: return self.RepoError(
            False,
            9,
            "You can only parse image id or post id",
            TypeError("Too many arguments got parsed")
        )
        self.logger.exception("Too many arguments got parsed")
        return self.get_all_enriched(
            table="messenger.images",
            primary_keys=("image_id", [(image_id, ) for image_id in image_ids]) if image_ids else ("post_id", [(post_id, ) for post_id in post_ids]),
            columns=["image_path"]
        )
    def delete_image(self, *image_ids: int) -> None | BaseRepo.RepoError:
        """Given a list of image_ids, deletes the corresponding images"""
        # making condition
        statement = ["%s" for _ in range(len(image_ids))]
        condition = f"WHERE image_id IN ({", ".join(statement)})"

        # getting delete query
        delete_query = self.build_delete_query(
            table="messenger.images",
            condition=condition
        )
        # executing statement
        return self.execute_write(delete_query, *image_ids)