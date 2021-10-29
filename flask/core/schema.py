schema = """
CREATE TABLE IF NOT EXISTS `action` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `name`                  VARCHAR(200) NOT NULL,
    PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `location` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `api_search_key`        VARCHAR(1000),
    `name`                  VARCHAR(200) NOT NULL UNIQUE,
    PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `photo` (
    `id`                    INT(11) NOT NULL AUTO_INCREMENT,
    `type`                  INT(3),
    `description`           VARCHAR(200),
    `image_id`              VARCHAR(1000) NOT NULL,
    `location_id`           INT(11),
    `datetime`              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `upload_datetime`       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`),
    CONSTRAINT FOREIGN KEY (`location_id`) REFERENCES `furfellas`.`location` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS `photo_action` (
    `photo_id`              INT(11),
    `action_id`             INT(11),
    CONSTRAINT FOREIGN KEY (`photo_id`) REFERENCES `furfellas`.`photo` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (`action_id`) REFERENCES `furfellas`.`action` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);
"""
