schema="""
CREATE TABLE IF NOT EXISTS `user` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(12) UNIQUE,
    `email`                 VARCHAR(100),
    `password`              VARCHAR(200) NOT NULL,
    `salt`                  VARCHAR(20) NOT NULL,
    `user_type`             INT(3) DEFAULT 2,
    `login_counting`        INT(5) DEFAULT 0,
    `create_datetime`       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `action` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(200) NOT NULL,
    PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `location` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `key`                   VARCHAR(1000),
    `name`                  VARCHAR(200) NOT NULL,
    PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `photo` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `type`                  INT(3),
    `action_id`             INT(11),
    `desc`                  VARCHAR(200) NOT NULL,
    `location_id`           INT(11),
    `file_name`             VARCHAR(1000) NOT NULL,
    `datetime`              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `upload_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`),
    CONSTRAINT FOREIGN KEY (`action_id`) REFERENCES `furfellas`.`action` (`id`) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT FOREIGN KEY (`location_id`) REFERENCES `furfellas`.`location` (`id`) ON UPDATE CASCADE ON DELETE SET NULL
);
"""

