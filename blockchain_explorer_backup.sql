-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: blockchain_explorer
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Current Database: `blockchain_explorer`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `blockchain_explorer` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `blockchain_explorer`;

--
-- Table structure for table `address`
--

DROP TABLE IF EXISTS `address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `address` (
  `address` varchar(42) NOT NULL,
  `address_type` varchar(20) NOT NULL,
  `current_balance` decimal(30,10) DEFAULT '0.0000000000',
  `last_seen` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`address`),
  CONSTRAINT `chk_address_type` CHECK ((`address_type` in (_utf8mb4'EOA',_utf8mb4'Contract')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `address`
--

LOCK TABLES `address` WRITE;
/*!40000 ALTER TABLE `address` DISABLE KEYS */;
INSERT INTO `address` VALUES ('0x1111111111111111111111111111111111111111','EOA',16.0000000000,'2026-09-01 04:30:00'),('0x2222222222222222222222222222222222222222','EOA',27.2500000000,'2026-09-02 05:30:00'),('0x3333333333333333333333333333333333333333','Contract',100.0000000000,'2026-09-03 06:30:00'),('0x4444444444444444444444444444444444444444','EOA',8.2500000000,'2026-09-04 07:30:00'),('0x5555555555555555555555555555555555555555','EOA',50.0000000000,'2026-09-05 08:30:00'),('0x6666666666666666666666666666666666666666','Contract',75.5000000000,'2026-09-06 09:30:00'),('0x7777777777777777777777777777777777777777','EOA',18.7500000000,'2026-09-07 10:30:00'),('0x8888888888888888888888888888888888888888','EOA',32.0000000000,'2026-09-08 11:30:00'),('0x9999999999999999999999999999999999999999','Contract',200.0000000000,'2026-09-09 12:30:00'),('0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','EOA',5.5000000000,'2026-09-10 13:30:00'),('0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','EOA',45.0000000000,'2026-09-11 04:30:00'),('0xcccccccccccccccccccccccccccccccccccccc','Contract',150.0000000000,'2026-09-12 05:30:00');
/*!40000 ALTER TABLE `address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `block`
--

DROP TABLE IF EXISTS `block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `block` (
  `block_number` bigint NOT NULL,
  `block_hash` varchar(66) NOT NULL,
  `timestamp` timestamp NOT NULL,
  `transaction_count` int DEFAULT '0',
  `gas_used` bigint DEFAULT '0',
  PRIMARY KEY (`block_number`),
  UNIQUE KEY `block_hash` (`block_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `block`
--

LOCK TABLES `block` WRITE;
/*!40000 ALTER TABLE `block` DISABLE KEYS */;
INSERT INTO `block` VALUES (100001,'0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','2026-09-01 04:30:00',2,210000),(100002,'0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','2026-09-02 05:30:00',2,280000),(100003,'0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','2026-09-03 06:30:00',2,150000),(100004,'0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd','2026-09-04 07:30:00',2,350000),(100005,'0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee','2026-09-05 08:30:00',2,420000),(100006,'0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff','2026-09-06 09:30:00',2,230000),(100007,'0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef','2026-09-07 10:30:00',2,300000),(100008,'0xabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd','2026-09-08 11:30:00',2,170000),(100009,'0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef','2026-09-09 12:30:00',2,390000),(100010,'0xfedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbabc','2026-09-10 13:30:00',2,250000);
/*!40000 ALTER TABLE `block` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blockchain_transaction`
--

DROP TABLE IF EXISTS `blockchain_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blockchain_transaction` (
  `tx_hash` varchar(66) NOT NULL,
  `amount` decimal(30,10) DEFAULT '0.0000000000',
  `gas_fee` decimal(30,10) DEFAULT '0.0000000000',
  `status` varchar(20) NOT NULL,
  `timestamp` timestamp NOT NULL,
  `block_number` bigint NOT NULL,
  `from_address` varchar(42) NOT NULL,
  `to_address` varchar(42) NOT NULL,
  PRIMARY KEY (`tx_hash`),
  KEY `block_number` (`block_number`),
  KEY `from_address` (`from_address`),
  KEY `to_address` (`to_address`),
  CONSTRAINT `blockchain_transaction_ibfk_1` FOREIGN KEY (`block_number`) REFERENCES `block` (`block_number`),
  CONSTRAINT `blockchain_transaction_ibfk_2` FOREIGN KEY (`from_address`) REFERENCES `address` (`address`),
  CONSTRAINT `blockchain_transaction_ibfk_3` FOREIGN KEY (`to_address`) REFERENCES `address` (`address`),
  CONSTRAINT `chk_tx_status` CHECK ((`status` in (_utf8mb4'Success',_utf8mb4'Failed',_utf8mb4'Pending')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blockchain_transaction`
--

LOCK TABLES `blockchain_transaction` WRITE;
/*!40000 ALTER TABLE `blockchain_transaction` DISABLE KEYS */;
INSERT INTO `blockchain_transaction` VALUES ('0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdee',18.0000000000,0.0040000000,'Success','2026-09-07 10:35:00',100007,'0x4444444444444444444444444444444444444444','0x5555555555555555555555555555555555555555'),('0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',3.5000000000,0.0012000000,'Success','2026-09-07 10:30:00',100007,'0x1111111111111111111111111111111111111111','0x4444444444444444444444444444444444444444'),('0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdee',9.5000000000,0.0027000000,'Success','2026-09-09 12:55:00',100009,'0x8888888888888888888888888888888888888888','0x9999999999999999999999999999999999999999'),('0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef',40.0000000000,0.0060000000,'Success','2026-09-09 12:50:00',100009,'0x7777777777777777777777777777777777777777','0x8888888888888888888888888888888888888888'),('0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',5.5000000000,0.0021000000,'Success','2026-09-01 04:35:00',100001,'0x1111111111111111111111111111111111111111','0x2222222222222222222222222222222222222222'),('0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab',8.2500000000,0.0025000000,'Success','2026-09-01 04:38:00',100001,'0x2222222222222222222222222222222222222222','0x3333333333333333333333333333333333333333'),('0xabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd',22.5000000000,0.0045000000,'Failed','2026-09-08 11:40:00',100008,'0x5555555555555555555555555555555555555555','0x6666666666666666666666666666666666666666'),('0xabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabce',6.7500000000,0.0022000000,'Pending','2026-09-08 11:45:00',100008,'0x6666666666666666666666666666666666666666','0x7777777777777777777777777777777777777777'),('0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',10.2500000000,0.0035000000,'Success','2026-09-02 05:40:00',100002,'0x3333333333333333333333333333333333333333','0x4444444444444444444444444444444444444444'),('0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbc',2.7500000000,0.0015000000,'Failed','2026-09-02 05:45:00',100002,'0x4444444444444444444444444444444444444444','0x5555555555555555555555555555555555555555'),('0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',20.0000000000,0.0045000000,'Success','2026-09-03 06:50:00',100003,'0x5555555555555555555555555555555555555555','0x6666666666666666666666666666666666666666'),('0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccd',3.7500000000,0.0018000000,'Pending','2026-09-03 06:55:00',100003,'0x6666666666666666666666666666666666666666','0x7777777777777777777777777777777777777777'),('0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',7.2500000000,0.0028000000,'Pending','2026-09-04 08:00:00',100004,'0x7777777777777777777777777777777777777777','0x8888888888888888888888888888888888888888'),('0xddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddde',15.7500000000,0.0032000000,'Success','2026-09-04 08:05:00',100004,'0x8888888888888888888888888888888888888888','0x9999999999999999999999999999999999999999'),('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',30.5000000000,0.0050000000,'Success','2026-09-05 09:10:00',100005,'0x9999999999999999999999999999999999999999','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeef',12.0000000000,0.0025000000,'Failed','2026-09-05 09:15:00',100005,'0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),('0xfedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbabc',25.0000000000,0.0048000000,'Success','2026-09-10 14:00:00',100010,'0x9999999999999999999999999999999999999999','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),('0xfedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbabd',11.2500000000,0.0031000000,'Failed','2026-09-10 14:05:00',100010,'0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),('0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe',4.2500000000,0.0017000000,'Success','2026-09-06 10:25:00',100006,'0xcccccccccccccccccccccccccccccccccccccc','0x1111111111111111111111111111111111111111'),('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',15.7500000000,0.0032000000,'Success','2026-09-06 10:20:00',100006,'0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','0xcccccccccccccccccccccccccccccccccccccc');
/*!40000 ALTER TABLE `blockchain_transaction` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `validate_transaction_amount` BEFORE INSERT ON `blockchain_transaction` FOR EACH ROW BEGIN
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction amount must be greater than zero';
    END IF;

    IF NEW.gas_fee < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Gas fee cannot be negative';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `token_transfer`
--

DROP TABLE IF EXISTS `token_transfer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_transfer` (
  `transfer_id` bigint NOT NULL AUTO_INCREMENT,
  `token_symbol` varchar(20) NOT NULL,
  `amount` decimal(40,18) NOT NULL,
  `timestamp` timestamp NOT NULL,
  `tx_hash` varchar(66) NOT NULL,
  `from_address` varchar(42) NOT NULL,
  `to_address` varchar(42) NOT NULL,
  PRIMARY KEY (`transfer_id`),
  KEY `tx_hash` (`tx_hash`),
  KEY `from_address` (`from_address`),
  KEY `to_address` (`to_address`),
  CONSTRAINT `token_transfer_ibfk_1` FOREIGN KEY (`tx_hash`) REFERENCES `blockchain_transaction` (`tx_hash`),
  CONSTRAINT `token_transfer_ibfk_2` FOREIGN KEY (`from_address`) REFERENCES `address` (`address`),
  CONSTRAINT `token_transfer_ibfk_3` FOREIGN KEY (`to_address`) REFERENCES `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_transfer`
--

LOCK TABLES `token_transfer` WRITE;
/*!40000 ALTER TABLE `token_transfer` DISABLE KEYS */;
INSERT INTO `token_transfer` VALUES (1,'USDT',1000.000000000000000000,'2026-09-01 04:35:30','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','0x1111111111111111111111111111111111111111','0x2222222222222222222222222222222222222222'),(2,'USDC',500.000000000000000000,'2026-09-01 04:38:30','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab','0x2222222222222222222222222222222222222222','0x3333333333333333333333333333333333333333'),(3,'DAI',750.000000000000000000,'2026-09-02 05:40:30','0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','0x3333333333333333333333333333333333333333','0x4444444444444444444444444444444444444444'),(4,'USDT',2500.000000000000000000,'2026-09-03 06:50:30','0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','0x5555555555555555555555555555555555555555','0x6666666666666666666666666666666666666666'),(5,'LINK',150.000000000000000000,'2026-09-04 08:00:30','0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd','0x7777777777777777777777777777777777777777','0x8888888888888888888888888888888888888888'),(6,'ETH',5.000000000000000000,'2026-09-04 08:05:30','0xddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddde','0x8888888888888888888888888888888888888888','0x9999999999999999999999999999999999999999'),(7,'UNI',300.000000000000000000,'2026-09-05 09:10:30','0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee','0x9999999999999999999999999999999999999999','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),(8,'USDC',1250.000000000000000000,'2026-09-06 10:20:30','0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff','0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','0xcccccccccccccccccccccccccccccccccccccc'),(9,'USDT',4000.000000000000000000,'2026-09-07 10:30:30','0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef','0x1111111111111111111111111111111111111111','0x4444444444444444444444444444444444444444'),(10,'DAI',800.000000000000000000,'2026-09-07 10:35:30','0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdee','0x4444444444444444444444444444444444444444','0x5555555555555555555555555555555555555555'),(11,'USDT',3500.000000000000000000,'2026-09-09 12:50:30','0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef','0x7777777777777777777777777777777777777777','0x8888888888888888888888888888888888888888'),(12,'USDC',600.000000000000000000,'2026-09-09 12:55:30','0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdee','0x8888888888888888888888888888888888888888','0x9999999999999999999999999999999999999999'),(13,'ETH',8.500000000000000000,'2026-09-10 14:00:30','0xfedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbabc','0x9999999999999999999999999999999999999999','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),(14,'LINK',450.000000000000000000,'2026-09-10 14:05:30','0xfedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbafedcbabd','0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb');
/*!40000 ALTER TABLE `token_transfer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `transaction_details`
--

DROP TABLE IF EXISTS `transaction_details`;
/*!50001 DROP VIEW IF EXISTS `transaction_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `transaction_details` AS SELECT 
 1 AS `tx_hash`,
 1 AS `amount`,
 1 AS `gas_fee`,
 1 AS `status`,
 1 AS `timestamp`,
 1 AS `block_number`,
 1 AS `from_address`,
 1 AS `to_address`,
 1 AS `block_hash`,
 1 AS `transaction_count`,
 1 AS `gas_used`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `role` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Arjun Sharma','arjun.sharma@gmail.com','Admin'),(2,'Rahul Kumar','rahul.kumar@gmail.com','Analyst'),(3,'Sneha Rao','sneha.rao@gmail.com','User'),(4,'Aditya Singh','aditya.singh@gmail.com','User'),(5,'Priya Nair','priya.nair@gmail.com','Analyst'),(6,'Karan Patel','karan.patel@gmail.com','User'),(7,'Ananya Das','ananya.das@gmail.com','User'),(8,'Rohit Verma','rohit.verma@gmail.com','Analyst'),(9,'Meera Iyer','meera.iyer@gmail.com','User'),(10,'Vikram Joshi','vikram.joshi@gmail.com','Admin');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `wallet_activity`
--

DROP TABLE IF EXISTS `wallet_activity`;
/*!50001 DROP VIEW IF EXISTS `wallet_activity`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `wallet_activity` AS SELECT 
 1 AS `address`,
 1 AS `address_type`,
 1 AS `current_balance`,
 1 AS `transaction_count`,
 1 AS `total_transaction_amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `watchlist`
--

DROP TABLE IF EXISTS `watchlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `watchlist` (
  `watchlist_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int NOT NULL,
  PRIMARY KEY (`watchlist_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `watchlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `watchlist`
--

LOCK TABLES `watchlist` WRITE;
/*!40000 ALTER TABLE `watchlist` DISABLE KEYS */;
INSERT INTO `watchlist` VALUES (1,'High Value Wallets','2026-10-03 15:59:49',1),(2,'DeFi Addresses','2026-10-03 15:59:49',2),(3,'Whale Tracking','2026-10-03 15:59:49',3),(4,'Exchange Wallets','2026-10-03 15:59:49',4),(5,'Smart Contracts','2026-10-03 15:59:49',5),(6,'Suspicious Addresses','2026-10-03 15:59:49',6),(7,'Token Monitoring','2026-10-03 15:59:49',7),(8,'Daily Transactions','2026-10-03 15:59:49',8),(9,'Large Transfers','2026-10-03 15:59:49',9),(10,'Research Wallets','2026-10-03 15:59:49',10);
/*!40000 ALTER TABLE `watchlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `watchlist_address`
--

DROP TABLE IF EXISTS `watchlist_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `watchlist_address` (
  `watchlist_address_id` int NOT NULL AUTO_INCREMENT,
  `added_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `watchlist_id` int NOT NULL,
  `address` varchar(42) NOT NULL,
  PRIMARY KEY (`watchlist_address_id`),
  UNIQUE KEY `watchlist_id` (`watchlist_id`,`address`),
  KEY `address` (`address`),
  CONSTRAINT `watchlist_address_ibfk_1` FOREIGN KEY (`watchlist_id`) REFERENCES `watchlist` (`watchlist_id`),
  CONSTRAINT `watchlist_address_ibfk_2` FOREIGN KEY (`address`) REFERENCES `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `watchlist_address`
--

LOCK TABLES `watchlist_address` WRITE;
/*!40000 ALTER TABLE `watchlist_address` DISABLE KEYS */;
INSERT INTO `watchlist_address` VALUES (1,'2026-10-03 16:01:33',1,'0x1111111111111111111111111111111111111111'),(2,'2026-10-03 16:01:33',1,'0x5555555555555555555555555555555555555555'),(3,'2026-10-03 16:01:33',2,'0x3333333333333333333333333333333333333333'),(4,'2026-10-03 16:01:33',2,'0x6666666666666666666666666666666666666666'),(5,'2026-10-03 16:01:33',3,'0x9999999999999999999999999999999999999999'),(6,'2026-10-03 16:01:33',3,'0xcccccccccccccccccccccccccccccccccccccc'),(7,'2026-10-03 16:01:33',4,'0x2222222222222222222222222222222222222222'),(8,'2026-10-03 16:01:33',4,'0x8888888888888888888888888888888888888888'),(9,'2026-10-03 16:01:33',5,'0x3333333333333333333333333333333333333333'),(10,'2026-10-03 16:01:33',5,'0x9999999999999999999999999999999999999999'),(11,'2026-10-03 16:01:33',6,'0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),(12,'2026-10-03 16:01:33',7,'0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),(13,'2026-10-03 16:01:33',8,'0x7777777777777777777777777777777777777777'),(14,'2026-10-03 16:01:33',9,'0x8888888888888888888888888888888888888888');
/*!40000 ALTER TABLE `watchlist_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'blockchain_explorer'
--

--
-- Dumping routines for database 'blockchain_explorer'
--
/*!50003 DROP PROCEDURE IF EXISTS `GetAddressTransactions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetAddressTransactions`(IN p_address VARCHAR(42))
BEGIN
    SELECT
        tx_hash,
        amount,
        gas_fee,
        status,
        timestamp,
        block_number,
        from_address,
        to_address
    FROM blockchain_transaction
    WHERE from_address = p_address
       OR to_address = p_address
    ORDER BY timestamp DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetBlockTransactions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetBlockTransactions`(IN p_block_number BIGINT)
BEGIN
    SELECT
        tx_hash,
        amount,
        gas_fee,
        status,
        timestamp,
        from_address,
        to_address
    FROM blockchain_transaction
    WHERE block_number = p_block_number;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `blockchain_explorer`
--

USE `blockchain_explorer`;

--
-- Final view structure for view `transaction_details`
--

/*!50001 DROP VIEW IF EXISTS `transaction_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `transaction_details` AS select `t`.`tx_hash` AS `tx_hash`,`t`.`amount` AS `amount`,`t`.`gas_fee` AS `gas_fee`,`t`.`status` AS `status`,`t`.`timestamp` AS `timestamp`,`t`.`block_number` AS `block_number`,`t`.`from_address` AS `from_address`,`t`.`to_address` AS `to_address`,`b`.`block_hash` AS `block_hash`,`b`.`transaction_count` AS `transaction_count`,`b`.`gas_used` AS `gas_used` from (`blockchain_transaction` `t` join `block` `b` on((`t`.`block_number` = `b`.`block_number`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `wallet_activity`
--

/*!50001 DROP VIEW IF EXISTS `wallet_activity`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `wallet_activity` AS select `a`.`address` AS `address`,`a`.`address_type` AS `address_type`,`a`.`current_balance` AS `current_balance`,count(`t`.`tx_hash`) AS `transaction_count`,coalesce(sum(`t`.`amount`),0) AS `total_transaction_amount` from (`address` `a` left join `blockchain_transaction` `t` on((`a`.`address` = `t`.`from_address`))) group by `a`.`address`,`a`.`address_type`,`a`.`current_balance` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-03  8:24:21
