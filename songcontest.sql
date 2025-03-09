-- MySQL dump 10.13  Distrib 9.1.0, for macos13.7 (arm64)
--
-- Host: localhost    Database: superagency
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `songCountry`
--

DROP TABLE IF EXISTS `songCountry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `songCountry` (
  `countryID` smallint NOT NULL AUTO_INCREMENT,
  `country` varchar(60) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `image` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` enum('0','1') COLLATE utf8mb4_general_ci NOT NULL DEFAULT '1',
  `display_order` smallint NOT NULL DEFAULT '1',
  PRIMARY KEY (`countryID`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `songCountry`
--

LOCK TABLES `songCountry` WRITE;
/*!40000 ALTER TABLE `songCountry` DISABLE KEYS */;
INSERT INTO `songCountry` VALUES (1,'Germany','static/uploads/germany.png','1',0),(2,'Hungary','static/uploads/hungary.png','1',0),(3,'Greece','static/uploads/greece.png','1',0),(4,'Ireland','static/uploads/ireland.png','1',0),(5,'Iceland','static/uploads/iceland.png','1',0),(6,'Italy','static/uploads/italy.png','1',0),(7,'Poland','static/uploads/poland.png','1',0),(8,'Sweden','static/uploads/sweden.png','1',0),(9,'Russia','static/uploads/russia.png','1',0),(10,'Norway','static/uploads/norway.png','1',0),(11,'India','static/uploads/india.png','1',0),(12,'Australia','static/uploads/australia.png','1',0),(13,'United Kingdom','static/uploads/uk.png','1',0),(14,'Argentina','static/uploads/argentina.png','1',0);
/*!40000 ALTER TABLE `songCountry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `songShowCountries`
--

DROP TABLE IF EXISTS `songShowCountries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `songShowCountries` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `showID` smallint NOT NULL,
  `countryID` smallint NOT NULL,
  `showOrder` tinyint NOT NULL DEFAULT '1',
  `votesFirst` smallint NOT NULL DEFAULT '0',
  `votesSecond` smallint NOT NULL DEFAULT '0',
  `votesThird` smallint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `countryID` (`countryID`),
  KEY `fk_showID` (`showID`),
  CONSTRAINT `fk_showID` FOREIGN KEY (`showID`) REFERENCES `songShows` (`showID`) ON DELETE CASCADE,
  CONSTRAINT `songshowcountries_ibfk_1` FOREIGN KEY (`showID`) REFERENCES `songShows` (`showID`) ON DELETE CASCADE,
  CONSTRAINT `songshowcountries_ibfk_2` FOREIGN KEY (`countryID`) REFERENCES `songCountry` (`countryID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `songShowCountries`
--

LOCK TABLES `songShowCountries` WRITE;
/*!40000 ALTER TABLE `songShowCountries` DISABLE KEYS */;
INSERT INTO `songShowCountries` VALUES (1,4,10,1,13,15,16),(2,4,8,4,12,14,19),(3,4,11,2,15,17,17),(4,4,12,5,14,12,14),(5,4,13,6,14,13,13),(6,4,14,3,16,16,11),(7,4,5,7,16,13,10),(8,5,10,1,1,0,0),(9,5,8,4,0,1,0),(10,5,11,2,0,0,0),(11,5,12,5,0,0,0),(12,5,13,6,0,0,1),(13,5,14,3,0,0,0),(14,5,5,7,0,0,0);
/*!40000 ALTER TABLE `songShowCountries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `songShows`
--

DROP TABLE IF EXISTS `songShows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `songShows` (
  `showID` smallint NOT NULL AUTO_INCREMENT,
  `showName` varchar(60) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `showDesc` tinytext COLLATE utf8mb4_general_ci,
  `showDate` date DEFAULT NULL,
  `totalContestants` tinyint NOT NULL DEFAULT '7',
  PRIMARY KEY (`showID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `songShows`
--

LOCK TABLES `songShows` WRITE;
/*!40000 ALTER TABLE `songShows` DISABLE KEYS */;
INSERT INTO `songShows` VALUES (1,'A Test Show','This is a description field','2025-01-09',7),(2,'Second Show','another test show','2025-04-17',11),(3,'A Test Show','Description of said show','2025-01-31',10),(4,'Adelaide Fringe Festival',NULL,'2025-03-19',7),(5,'Song Contest Test Show',NULL,'2025-03-09',7);
/*!40000 ALTER TABLE `songShows` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `superTest`
--

DROP TABLE IF EXISTS `superTest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `superTest` (
  `superID` tinyint NOT NULL AUTO_INCREMENT,
  `superName` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `superPassword` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `superEmail` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `superRole` char(5) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`superID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `superTest`
--

LOCK TABLES `superTest` WRITE;
/*!40000 ALTER TABLE `superTest` DISABLE KEYS */;
INSERT INTO `superTest` VALUES (1,'SUPER AGENT','test1234','support@superagency.pro','admin'),(2,'SEA2','$2b$12$C2hdL5MQbR048.R.zvbWguJG2Fkklerx6xDC3kn1ejMEVWMejd5Hq','sea@gashe.com','user'),(3,'another test','testpassword','universalsea@gmail.com','user'),(4,'NEWTEST3','$2b$12$7l17AHBnqAZQWHONFPVVuex1xbWlVAEMc2As.xzK6TRS2IrzEFle.','test@test.com','user'),(5,'TESTER','$2b$12$ChHiX53DQZT/K4RdZ5fjFexKW3vyofp6Y8fdkQp1dtnXAqndjqIGS','sea@test.com','admin'),(6,'ANOTHER SILLY TEST','$2b$12$C9APP3FLylQReNMYXgJF4.gJGuQ5L0jI88yPytt2gjANkAy5sHyLG','silly@test.com','user');
/*!40000 ALTER TABLE `superTest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveyQuestions`
--

DROP TABLE IF EXISTS `surveyQuestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveyQuestions` (
  `questionID` int NOT NULL AUTO_INCREMENT,
  `survey_id` int DEFAULT NULL,
  `question_text` text COLLATE utf8mb4_general_ci NOT NULL,
  `question_type` enum('select_field','multiple_choice','scale','open_ended') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `options` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`questionID`),
  KEY `survey_id` (`survey_id`),
  CONSTRAINT `surveyquestions_ibfk_1` FOREIGN KEY (`survey_id`) REFERENCES `surveys` (`surveyID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveyQuestions`
--

LOCK TABLES `surveyQuestions` WRITE;
/*!40000 ALTER TABLE `surveyQuestions` DISABLE KEYS */;
INSERT INTO `surveyQuestions` VALUES (1,1,'Please introduce yourself and your project / enterprise','open_ended','null'),(2,1,'What are the biggest challenges or problems you’re currently facing in your business/project?','open_ended','null'),(3,1,'What specific goals or outcomes are you hoping to achieve?','open_ended','null'),(4,1,'Do you have any existing processes or systems that you feel could be improved or automated?','open_ended','null'),(5,1,'Have you used any AI tools or platforms before? If yes, which ones?','open_ended','null'),(6,1,'What do you like most about the AI tools you’ve used?','open_ended','null'),(7,1,'What frustrations or limitations have you encountered with AI tools?','open_ended','null'),(8,1,'On a scale of 1-10, how comfortable are you with adopting AI solutions in your business/project?','scale','null'),(9,1,'If you could design your dream AI system, what would it do? Please describe its features and capabilities.','open_ended','null'),(10,1,'What is your estimated budget for implementing an AI solution? ','open_ended','null'),(11,1,'How soon are you looking to implement an AI solution?','open_ended','null'),(12,1,'Would you like to schedule a free consultation to discuss how AI Super Agency can help you achieve your goals?','open_ended','null'),(13,1,'Please provide your contact information so we can follow up with you','open_ended','null');
/*!40000 ALTER TABLE `surveyQuestions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveyResponses`
--

DROP TABLE IF EXISTS `surveyResponses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveyResponses` (
  `responseID` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `question_id` int DEFAULT NULL,
  `answer` mediumtext COLLATE utf8mb4_general_ci,
  `responded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`responseID`),
  KEY `question_id` (`question_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `surveyresponses_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `surveyQuestions` (`questionID`),
  CONSTRAINT `surveyresponses_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `surveyUsers` (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveyResponses`
--

LOCK TABLES `surveyResponses` WRITE;
/*!40000 ALTER TABLE `surveyResponses` DISABLE KEYS */;
INSERT INTO `surveyResponses` VALUES (1,NULL,1,'We will also need contact details','2025-02-11 02:06:33'),(2,NULL,2,'AI help','2025-02-11 02:06:33'),(3,NULL,3,'Field test','2025-02-11 02:06:33'),(4,NULL,4,'Field test 2','2025-02-11 02:06:33'),(5,NULL,5,' Field test 3','2025-02-11 02:06:33'),(6,NULL,6,'Field test 4','2025-02-11 02:06:33'),(7,NULL,7,'Field test 5','2025-02-11 02:06:33'),(8,NULL,8,'6','2025-02-11 02:06:33'),(9,NULL,9,'everything','2025-02-11 02:06:33'),(10,NULL,10,'and more','2025-02-11 02:06:33'),(11,NULL,11,'right now','2025-02-11 02:06:33'),(12,NULL,12,'ok sure','2025-02-11 02:06:33'),(13,NULL,13,'Here we go - separate into multiple fields','2025-02-11 02:06:33');
/*!40000 ALTER TABLE `surveyResponses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveys`
--

DROP TABLE IF EXISTS `surveys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveys` (
  `surveyID` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`surveyID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveys`
--

LOCK TABLES `surveys` WRITE;
/*!40000 ALTER TABLE `surveys` DISABLE KEYS */;
INSERT INTO `surveys` VALUES (1,'The Survey of Surveys','The first test - edit test','2025-02-04 05:17:05');
/*!40000 ALTER TABLE `surveys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveyUsers`
--

DROP TABLE IF EXISTS `surveyUsers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveyUsers` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact_info` mediumtext COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveyUsers`
--

LOCK TABLES `surveyUsers` WRITE;
/*!40000 ALTER TABLE `surveyUsers` DISABLE KEYS */;
/*!40000 ALTER TABLE `surveyUsers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `superID` int NOT NULL AUTO_INCREMENT,
  `superName` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `superPassword` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `superRole` char(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`superID`),
  UNIQUE KEY `username` (`superName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-08 12:58:13
