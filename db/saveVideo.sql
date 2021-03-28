DELIMITER //
DROP PROCEDURE IF EXISTS saveVideo //

CREATE PROCEDURE saveVideo(IN UserIdIn INT, IN VideoNameIn varchar(250), IN VideoPathIn TEXT, IN DescriptionIn TEXT)
BEGIN
INSERT INTO videos (user_id, name, video, description) VALUES (UserIdIn, VideoNameIn, VideoPathIn, DescriptionIn);
SELECT LAST_INSERT_ID();
END//
DELIMITER ;