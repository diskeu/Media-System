-- migration to add session and refresh token tables

-- Refresh Tokens
CREATE TABLE IF NOT EXISTS messenger.refresh_cookies (
    cookie_hash BINARY(64) NOT NULL,       -- Sha(512)
    user_id INT NOT NULL,
    c_expiry_date TIMESTAMP NOT NULL,

    -- Foreign / Primary Keys
    CONSTRAINT cookie_h_refresh_p PRIMARY KEY
    (cookie_hash),
    CONSTRAINT user_id_refresh_fk FOREIGN KEY (user_id)
    REFERENCES messenger.users(user_id)
        ON DELETE CASCADE
) DEFAULT CHARACTER SET latin1 -- Reducing on 64 BYTES instead of 256 BYTES
;
-- expiry date trigger
DELIMITER $$
CREATE TRIGGER expiry_date_refresh
BEFORE INSERT ON messenger.refresh_cookies
FOR EACH ROW
BEGIN
    IF NEW.c_expiry_date IS NULL THEN
        SET NEW.c_expiry_date = DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 DAY);
    END IF;
END $$
DELIMITER ;

-- Session Tokens
CREATE TABLE IF NOT EXISTS messenger.session_cookies (
    cookie_hash BINARY(32) NOT NULL,        -- Sha(256)
    user_id INT NOT NULL,
    c_expiry_date TIMESTAMP NOT NULL,

    -- Foreign / Primary Keys
    CONSTRAINT cookie_h_session_p PRIMARY KEY
    (cookie_hash),
    CONSTRAINT user_id_session_fk FOREIGN KEY (user_id)
    REFERENCES messenger.users(user_id)
        ON DELETE CASCADE
) DEFAULT CHARACTER SET latin1 -- Reducing on 32 BYTES instead of 128 BYTES
;
-- expiry date trigger
DELIMITER $$
CREATE TRIGGER expiry_date_session
BEFORE INSERT ON messenger.session_cookies
FOR EACH ROW
BEGIN
    IF NEW.c_expiry_date IS NULL THEN
        SET NEW.c_expiry_date = DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR);
    END IF ;
END $$
DELIMITER ;