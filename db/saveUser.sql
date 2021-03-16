DELIMITER //
DROP PROCEDURE IF EXISTS saveUser //

CREATE PROCEDURE saveUser(IN UsernameIn varchar(50))
BEGIN
INSERT INTO users (username) VALUES (UsernameIn);
SELECT LAST_INSERT_ID();
END//
DELIMITER ;