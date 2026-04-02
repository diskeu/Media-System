-- Deletes the Session Cookies table. Only uses more securer version with Acces and Refresh Tokens
DROP TRIGGER IF EXISTS expiry_date_session;
DROP TABLE IF EXISTS messenger.session_cookies;

-- rename Table
ALTER TABLE messenger.refresh_tokens
    RENAME TO refresh_tokens
;
-- rename Columns
ALTER TABLE messenger.refresh_tokens
    RENAME COLUMN token_hash TO token_hash
;
ALTER TABLE messenger.refresh_tokens
    RENAME COLUMN t_expiry_date TO t_expiry_date
;
-- rename PRIMARY KEY
ALTER TABLE messenger.refresh_tokens
    DROP PRIMARY KEY
;
ALTER TABLE messenger.refresh_tokens
    ADD CONSTRAINT refresh_token_hash_p
        PRIMARY KEY (token_hash)
;