DROP TABLE IF EXISTS videos;
CREATE TABLE videos (
    video_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    name varchar(250) NOT NULL,
    video LONGBLOB NOT NULL,
    description TEXT,
    PRIMARY KEY (video_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);