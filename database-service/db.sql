/***CREATING ALL TABLES*/
CREATE TABLE `projects` (
  `uuid` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `createdAt` DATETIME NOT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=INNODB;
CREATE TABLE `experiments` (
  `uuid` VARCHAR(255) NOT NULL,
  `projectId` VARCHAR(255) NOT NULL,
  `pipelineId` VARCHAR(255) NOT NULL,
  `datasetId` VARCHAR(255) NOT NULL,
  `targetColumnId` VARCHAR(255),
  `parameters` LONGTEXT NOT NULL,
  `createdAt` DATETIME NOT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=INNODB;
CREATE TABLE `pipelines`
(
  `uuid` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=INNODB;
CREATE TABLE `datasets`
(
  `uuid` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=INNODB;
CREATE TABLE `columns`
(
  `uuid` VARCHAR(255) NOT NULL,
  `datasetId` VARCHAR(255) NOT NULL,
  `dataType` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=INNODB;

/******************************************************************/