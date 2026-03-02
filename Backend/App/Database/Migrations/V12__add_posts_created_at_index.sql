-- Adding index for the created-at column in the posts table

CREATE INDEX created_at_idx
ON messenger.posts (created_at);