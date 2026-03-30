-- Update Trigger
DROP TRIGGER expiry_date_refresh;

DELIMITER $$
CREATE TRIGGER expiry_date_refresh
BEFORE INSERT ON messenger.refresh_tokens
FOR EACH ROW
BEGIN
    IF NEW.t_expiry_date IS NULL THEN
        SET NEW.t_expiry_date = DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 DAY);
    END IF;
END $$
DELIMITER ;