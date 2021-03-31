DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username varchar(50) NOT NULL UNIQUE,
    PRIMARY KEY (user_id)
);