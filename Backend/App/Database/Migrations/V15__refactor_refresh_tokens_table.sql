-- Refactor the oversimplified refresh_tokens table

-- Drop old Primary Key(refresh_token_hash_p)
ALTER TABLE messenger.refresh_tokens
DROP PRIMARY KEY
;
-- Create New Index On refresh_token_hash_p
CREATE INDEX IF NOT EXISTS token_hash_i
ON messenger.refresh_tokens(token_hash)
;

-- Add New columns
ALTER TABLE messenger.refresh_tokens
ADD COLUMN token_id INT NOT NULL AUTO_INCREMENT,
ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN revoked_at TIMESTAMP NULL DEFAULT NULL,
ADD COLUMN replaced_by INT NULL DEFAULT NULL,
ADD CONSTRAINT token_id_p -- Add new primary key
    PRIMARY KEY (token_id)
;

-- Add new foreign key
ALTER TABLE messenger.refresh_tokens
ADD CONSTRAINT replaced_by_fk
    FOREIGN KEY (replaced_by)
    REFERENCES messenger.refresh_tokens(token_id)
        ON DELETE SET NULL
;