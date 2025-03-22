/*
SQLyog Ultimate v10.00 Beta1
MySQL - 5.5.5-10.4.32-MariaDB : Database - glamorosa_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`glamorosa_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `glamorosa_db`;

/*Table structure for table `appointment_requests` */

DROP TABLE IF EXISTS `appointment_requests`;

CREATE TABLE `appointment_requests` (
  `appointment_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `preferred_date` date NOT NULL,
  `preferred_time` time NOT NULL,
  `inspiration_image` varchar(255) NOT NULL,
  `budget_range` decimal(10,2) NOT NULL,
  `special_requirements` text DEFAULT NULL,
  `status` enum('pending','approved','rejected','completed') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status_note` text DEFAULT NULL,
  PRIMARY KEY (`appointment_id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `appointment_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `appointment_requests_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `appointment_requests` */

LOCK TABLES `appointment_requests` WRITE;

insert  into `appointment_requests`(`appointment_id`,`user_id`,`category_id`,`description`,`preferred_date`,`preferred_time`,`inspiration_image`,`budget_range`,`special_requirements`,`status`,`created_at`,`updated_at`,`status_note`) values (6,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','approved','2025-02-16 21:12:36','2025-02-18 06:15:44',''),(9,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','pending','2025-02-16 21:12:36','2025-02-18 06:10:40','');

UNLOCK TABLES;

/*Table structure for table `appointments` */

DROP TABLE IF EXISTS `appointments`;

CREATE TABLE `appointments` (
  `appointment_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `appointment_date` date NOT NULL,
  `appointment_time` time NOT NULL,
  `inspiration_image` varchar(255) NOT NULL,
  `budget_range` decimal(10,2) NOT NULL,
  `special_requirements` text DEFAULT NULL,
  `status` enum('processing','shipped','completed') DEFAULT 'processing',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `original_request_id` int(11) NOT NULL,
  PRIMARY KEY (`appointment_id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`),
  KEY `original_request_id` (`original_request_id`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`original_request_id`) REFERENCES `appointment_requests` (`appointment_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `appointments` */

LOCK TABLES `appointments` WRITE;

insert  into `appointments`(`appointment_id`,`user_id`,`category_id`,`description`,`appointment_date`,`appointment_time`,`inspiration_image`,`budget_range`,`special_requirements`,`status`,`created_at`,`updated_at`,`original_request_id`) values (15,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','processing','2025-02-18 06:08:44','2025-02-18 06:08:44',6),(16,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','processing','2025-02-18 06:09:21','2025-02-18 06:09:21',6),(17,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','processing','2025-02-18 06:12:37','2025-02-18 06:12:37',6),(18,2,8,'a black barong with detailed gold lining','2025-02-17','09:00:00','uploads/appointments/inspiration_2_20250216211236_black_silk_barong.jpg','8000.00','Willing to add more if needed','processing','2025-02-18 06:15:44','2025-02-18 06:15:44',6);

UNLOCK TABLES;

/*Table structure for table `categories` */

DROP TABLE IF EXISTS `categories`;

CREATE TABLE `categories` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `categories` */

LOCK TABLES `categories` WRITE;

insert  into `categories`(`category_id`,`name`,`created_at`) values (1,'Suit','2025-02-13 01:40:38'),(2,'Gowns','2025-02-13 01:40:38'),(3,'Dress','2025-02-13 01:40:38'),(8,'Barong','2025-02-14 19:02:55');

UNLOCK TABLES;

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  `size` varchar(50) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` enum('GCASH','CASH') NOT NULL,
  `delivery_method` enum('delivery','pickup') NOT NULL,
  `order_status` enum('pending','processing','completed','cancelled') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `gcash_reference` varchar(100) DEFAULT NULL,
  `payment_proof` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  KEY `address_id` (`address_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`address_id`) REFERENCES `user_addresses` (`address_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders` */

LOCK TABLES `orders` WRITE;

insert  into `orders`(`order_id`,`user_id`,`product_id`,`address_id`,`size`,`quantity`,`total_amount`,`payment_method`,`delivery_method`,`order_status`,`created_at`,`gcash_reference`,`payment_proof`) values (2,2,16,4,'L',1,'8000.00','GCASH','delivery','completed','2025-02-14 20:57:01','123456789','uploads/payments/proof\\order_2_20250214205701.jpg'),(3,3,15,5,'L',1,'15000.00','GCASH','delivery','pending','2025-02-15 07:05:39','09123456789','uploads/payments/proof\\order_3_20250215070539.png'),(4,3,15,6,'L',1,'15000.00','CASH','pickup','completed','2025-02-15 07:06:07',NULL,NULL),(5,2,5,4,'XL',1,'10000.00','GCASH','delivery','completed','2025-02-17 07:44:07','123456789','uploads/payments/proof\\order_2_20250217074407.png');

UNLOCK TABLES;

/*Table structure for table `product_images` */

DROP TABLE IF EXISTS `product_images`;

CREATE TABLE `product_images` (
  `image_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `is_primary` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`image_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `product_images` */

LOCK TABLES `product_images` WRITE;

insert  into `product_images`(`image_id`,`product_id`,`image_path`,`is_primary`,`created_at`) values (7,5,'uploads/products/5_Dark_Gray_Suit.jpg',1,'2025-02-14 18:18:16'),(8,6,'uploads/products/6_Brownish_Suit.jpg',1,'2025-02-14 18:18:57'),(9,7,'uploads/products/7_gray_suit.jpg',1,'2025-02-14 18:19:26'),(10,8,'uploads/products/8_bluish_gown.jpg',1,'2025-02-14 18:24:13'),(11,9,'uploads/products/9_lavender_brown.jpg',1,'2025-02-14 18:42:19'),(12,10,'uploads/products/10_redish_gown.jpg',1,'2025-02-14 18:43:48'),(13,11,'uploads/products/11_pinkish_dress.jpg',1,'2025-02-14 18:58:18'),(14,12,'uploads/products/12_white_dress.jpg',1,'2025-02-14 18:59:07'),(15,13,'uploads/products/13_red_dress.jpg',1,'2025-02-14 19:15:08'),(16,14,'uploads/products/14_Teal_Green.png',1,'2025-02-14 19:17:06'),(17,15,'uploads/products/15_Axle_Gray.png',1,'2025-02-14 19:45:34'),(18,16,'uploads/products/16_White_Barong.jpg',1,'2025-02-14 19:46:05'),(19,17,'uploads/products/17_Light_Blue.png',1,'2025-02-14 19:46:45'),(20,18,'uploads/products/18_Benson_Crimson.png',1,'2025-02-14 19:47:49'),(21,19,'uploads/products/19_Black_dress.jpg',1,'2025-02-15 07:16:19');

UNLOCK TABLES;

/*Table structure for table `product_sizes` */

DROP TABLE IF EXISTS `product_sizes`;

CREATE TABLE `product_sizes` (
  `size_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `size` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`size_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_sizes_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `product_sizes` */

LOCK TABLES `product_sizes` WRITE;

insert  into `product_sizes`(`size_id`,`product_id`,`size`,`created_at`) values (4,5,'XL','2025-02-14 18:18:16'),(5,6,'L','2025-02-14 18:18:57'),(6,7,'M','2025-02-14 18:19:26'),(7,8,'M','2025-02-14 18:24:13'),(8,9,'L','2025-02-14 18:42:19'),(9,10,'L','2025-02-14 18:43:48'),(10,11,'M','2025-02-14 18:58:18'),(11,12,'L','2025-02-14 18:59:07'),(12,13,'L','2025-02-14 19:15:08'),(13,14,'L','2025-02-14 19:17:06'),(14,15,'L','2025-02-14 19:45:34'),(15,16,'L','2025-02-14 19:46:05'),(16,17,'S','2025-02-14 19:46:45'),(17,18,'S','2025-02-14 19:47:49'),(18,19,'S','2025-02-15 07:16:19');

UNLOCK TABLES;

/*Table structure for table `products` */

DROP TABLE IF EXISTS `products`;

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `regular_price` decimal(10,2) NOT NULL,
  `rental_fee_per_day` decimal(10,2) NOT NULL,
  `color` varchar(50) DEFAULT NULL,
  `material` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`product_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

LOCK TABLES `products` WRITE;

insert  into `products`(`product_id`,`name`,`category_id`,`description`,`regular_price`,`rental_fee_per_day`,`color`,`material`,`created_at`,`updated_at`) values (5,'Dark Gray Suit',1,'a Dark Gray Suit!','10000.00','500.00','Dark Gray','Cotton','2025-02-14 18:18:16','2025-02-14 18:18:16'),(6,'Brownish Suit',1,'a Brown Suit','12000.00','600.00','Brown','Cotton','2025-02-14 18:18:57','2025-02-14 18:18:57'),(7,'Gray Suit',1,'a Gray Suit','11100.00','550.00','Gray','Cotton','2025-02-14 18:19:26','2025-02-14 18:21:00'),(8,'Bluish Gown',2,'a Bluish Gown','17000.00','800.00','Blue','Cotton','2025-02-14 18:24:13','2025-02-14 18:24:13'),(9,'Lavender Gown',2,'Lavender Gown','14000.00','900.00','Lavender','Cotton','2025-02-14 18:42:19','2025-02-14 18:42:19'),(10,'Redish Gown',2,'a redish Gown','15000.00','1000.00','Red','Cotton','2025-02-14 18:43:48','2025-02-14 18:43:48'),(11,'Pinkish Dress',3,'a pinkish Dress','12000.00','500.00','Pink','Cotton','2025-02-14 18:58:18','2025-02-14 18:58:18'),(12,'White Dress',3,'a White Dress ','15000.00','750.00','White','Cotton','2025-02-14 18:59:07','2025-02-14 18:59:07'),(13,'Red Dress',3,'a Red Dress ','15000.00','800.00','Red','Cotton','2025-02-14 19:15:08','2025-02-14 19:15:08'),(14,'Teal Green Barong',8,'a Teal Green Barong','12000.00','700.00','Teal Green','Cotton','2025-02-14 19:17:06','2025-02-14 19:17:06'),(15,'Axle Gray Barong',8,'an Axle Gray Barong','15000.00','700.00','Axle Gray','Cotton','2025-02-14 19:45:34','2025-02-14 19:45:34'),(16,'White Barong',8,'a white barong ','8000.00','400.00','White','Cotton','2025-02-14 19:46:05','2025-02-14 19:46:05'),(17,'Light Blue Barong',8,'a light blue barong','11000.00','600.00','Light Blue','Cotton','2025-02-14 19:46:45','2025-02-14 19:46:45'),(18,'Benson Crimson Barong',8,'a benson crimson barong ','14000.00','1000.00','Benson Crimsom','Cotton','2025-02-14 19:47:49','2025-02-15 06:11:27'),(19,'Black Silk Dress',3,'There is a  story behind this classic long black dress. It will not serve you breakfast in bed, but it will always be there for you and will never disappoint you. You will definitely be happy together.','1500.00','300.00','Black','Cotton','2025-02-15 07:16:19','2025-02-15 07:16:19');

UNLOCK TABLES;

/*Table structure for table `rental_requests` */

DROP TABLE IF EXISTS `rental_requests`;

CREATE TABLE `rental_requests` (
  `request_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `size` varchar(50) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `rental_days` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `payment_method` enum('GCASH','CASH') NOT NULL,
  `valid_id_path` varchar(255) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status_note` text DEFAULT NULL,
  `gcash_reference` varchar(100) DEFAULT NULL,
  `payment_proof` varchar(255) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`request_id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `rental_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `rental_requests_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `rental_requests` */

LOCK TABLES `rental_requests` WRITE;

insert  into `rental_requests`(`request_id`,`user_id`,`product_id`,`size`,`start_date`,`end_date`,`rental_days`,`full_name`,`contact_number`,`address`,`payment_method`,`valid_id_path`,`status`,`created_at`,`status_note`,`gcash_reference`,`payment_proof`,`total_amount`) values (11,2,18,'S','2025-02-22','2025-03-22',28,'Acovera, Lyka Marie F.','09085062503','#888 E, Taelon St.','GCASH','uploads/products/valid_ids/valid_id_2_20250218003902_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','pending','2025-02-18 00:39:02',NULL,'12312','uploads/payments/proof\\rental_2_20250218003902.jpg','28000.00'),(12,2,16,'L','2025-02-22','2025-03-22',28,'Acovera, Lyka Marie F.','09085062503','#888 E, Taelon St.','GCASH','uploads/products/valid_ids/valid_id_2_20250218004228_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','pending','2025-02-18 00:42:28',NULL,'123456','uploads/payments/proof\\rental_2_20250218004228.jpg','11200.00');

UNLOCK TABLES;

/*Table structure for table `rentals` */

DROP TABLE IF EXISTS `rentals`;

CREATE TABLE `rentals` (
  `rental_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `size` varchar(50) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `rental_days` int(11) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `status` enum('processing','shipped','delivered','returned','completed','cancelled') DEFAULT 'processing',
  `customer_name` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `valid_id_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `return_date` date DEFAULT NULL,
  `days_late` int(11) DEFAULT 0,
  `late_fee` decimal(10,2) DEFAULT 0.00,
  `final_amount` decimal(10,2) DEFAULT 0.00,
  `payment_method` enum('GCASH','CASH') DEFAULT NULL,
  `gcash_reference` varchar(100) DEFAULT NULL,
  `payment_proof` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`rental_id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `rentals_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `rentals_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `rentals` */

LOCK TABLES `rentals` WRITE;

insert  into `rentals`(`rental_id`,`product_id`,`user_id`,`size`,`start_date`,`end_date`,`rental_days`,`total_amount`,`status`,`customer_name`,`contact_number`,`address`,`valid_id_path`,`created_at`,`return_date`,`days_late`,`late_fee`,`final_amount`,`payment_method`,`gcash_reference`,`payment_proof`) values (6,17,2,'S','2025-02-14','2025-02-16',2,'1200.00','processing','Acovera, Lyka Marie F.','09085062503','#888 E, Taelon St.','uploads/products/valid_ids/valid_id_2_20250215055334_pfp.jpg','2025-02-15 05:53:44',NULL,0,'0.00','0.00','GCASH','123456','uploads/payments/proof\\rental_2_20250215055334.jpg'),(7,14,3,'L','2025-02-15','2025-02-17',3,'2100.00','completed','Test Buyer','09123456789','#0123 Test St, Test Barangay, Test Municipality, Test Region','uploads/products/valid_ids/valid_id_3_20250215070959_ID.jpg','2025-02-15 07:21:49',NULL,0,'0.00','0.00','GCASH','123456789','uploads/payments/proof\\rental_3_20250215070959.png'),(8,5,2,'XL','2025-02-14','2025-02-17',5,'2500.00','returned','Acovera, Lyka Marie F.','09085062503','#888 E, Taelon St.','uploads/products/valid_ids/valid_id_2_20250214210834_pfp.jpg','2025-02-15 07:21:52',NULL,0,'0.00','0.00','GCASH','123456','uploads/payments/proof\\rental_2_20250214210834.jpg'),(9,14,3,'L','2025-02-15','2025-02-18',3,'2100.00','processing','Test Buyer','09123456789','#0123 Test St, Test Barangay, Test Municipality, Test Region','uploads/products/valid_ids/valid_id_3_20250215070857_bluish_gown.jpg','2025-02-16 21:54:57',NULL,0,'0.00','0.00','CASH',NULL,NULL);

UNLOCK TABLES;

/*Table structure for table `reservation_requests` */

DROP TABLE IF EXISTS `reservation_requests`;

CREATE TABLE `reservation_requests` (
  `request_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `size` varchar(10) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` enum('GCASH','CASH') NOT NULL,
  `gcash_reference` varchar(50) DEFAULT NULL,
  `valid_id_path` varchar(255) NOT NULL,
  `payment_proof` varchar(255) NOT NULL,
  `status` enum('pending','approved','rejected','completed') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`request_id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `reservation_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `reservation_requests_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `reservation_requests` */

LOCK TABLES `reservation_requests` WRITE;

insert  into `reservation_requests`(`request_id`,`user_id`,`product_id`,`size`,`full_name`,`contact_number`,`address`,`total_amount`,`payment_method`,`gcash_reference`,`valid_id_path`,`payment_proof`,`status`,`created_at`,`updated_at`) values (3,2,18,'S','Lem Fulgencio','09085062503','#888 E, Taelon St.','7000.00','GCASH','123456','uploads/products/valid_ids\\valid_id_2_20250218003113_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','uploads/payments/proof\\payment_2_20250218003113_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','pending','2025-02-18 00:31:13','2025-02-18 00:31:13');

UNLOCK TABLES;

/*Table structure for table `reservations` */

DROP TABLE IF EXISTS `reservations`;

CREATE TABLE `reservations` (
  `reservation_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `size` varchar(10) DEFAULT NULL,
  `full_name` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `gcash_reference` varchar(50) DEFAULT NULL,
  `valid_id_path` varchar(255) DEFAULT NULL,
  `payment_proof` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'processing',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`reservation_id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `reservations` */

LOCK TABLES `reservations` WRITE;

insert  into `reservations`(`reservation_id`,`user_id`,`product_id`,`size`,`full_name`,`contact_number`,`address`,`total_amount`,`payment_method`,`gcash_reference`,`valid_id_path`,`payment_proof`,`status`,`created_at`,`updated_at`) values (1,2,16,'L','Lem Fulgencio','09085062503','#888 E, Taelon St.','4000.00','GCASH','123456','uploads/products/valid_ids\\valid_id_2_20250217234956_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','uploads/payments/proof\\payment_2_20250217234956_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','processing','2025-02-18 00:22:51','2025-02-18 00:22:51'),(2,2,18,'S','Lem Fulgencio','09085062503','#888 E, Taelon St.','7000.00','GCASH','123456','uploads/products/valid_ids\\valid_id_2_20250218003113_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','uploads/payments/proof\\payment_2_20250218003113_56d5e7ae-e56d-4eec-a228-3687385833bb.jpg','processing','2025-02-18 06:06:59','2025-02-18 06:06:59');

UNLOCK TABLES;

/*Table structure for table `user_addresses` */

DROP TABLE IF EXISTS `user_addresses`;

CREATE TABLE `user_addresses` (
  `address_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `complete_address` text NOT NULL,
  `is_default` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`address_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `user_addresses` */

LOCK TABLES `user_addresses` WRITE;

insert  into `user_addresses`(`address_id`,`user_id`,`full_name`,`contact_number`,`complete_address`,`is_default`,`created_at`) values (4,2,'Acovera, Lyka Marie F.','09085062503','#888 E, Taelon St.',0,'2025-02-13 19:10:31'),(5,3,'Test Buyer','09123456789','#0123 Test St, Test Barangay, Test Municipality, Test Region',0,'2025-02-15 07:05:39'),(6,3,'Test Buyer','09123456789','#0123 Test St, Test Barangay, Test Municipality, Test Region',0,'2025-02-15 07:06:07');

UNLOCK TABLES;

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','buyer') DEFAULT 'buyer',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `users` */

LOCK TABLES `users` WRITE;

insert  into `users`(`user_id`,`full_name`,`email`,`phone_number`,`password_hash`,`role`,`created_at`,`updated_at`) values (1,'admin','admin@admin.com','09123456789','scrypt:32768:8:1$fHkLHPM38xXtd8xe$abd6bd75e44cf4536345d4717ed68286fc520150462d10e18c1fd5134c99a2752490b0fc62464a997aff68f47d9d9b64706f7cc565bddf1e396c5b3584f6f48a','admin','2025-02-13 00:57:40','2025-02-13 00:57:57'),(2,'Lem Fulgencio','lemfulgencio@gmail.com','09085062503','scrypt:32768:8:1$004W3gw0Z33Ik5vw$9f1f7b3b0e3363ef2b2947414350e6b58e1efcec09c21e3b41f9f780217585f775d8e95b85dc951d19887a8c400ad82cabbe3cc80e495e4b8d4b71db6963ffba','buyer','2025-02-13 02:14:37','2025-02-13 02:14:37'),(3,'Test Buyer','testbuyer@email.com','09123456789','scrypt:32768:8:1$MZnfti5drvuaRhYn$f56a1e4ed4282eccce9efab4db97e2fd85444efef1b274008bd60e0c0984f06819e6fd0bdeb004ac8560861b68a444b3e3b21022f73343316fa82df8b23677ab','buyer','2025-02-15 07:02:31','2025-02-15 07:02:31');

UNLOCK TABLES;

/*Table structure for table `wishlists` */

DROP TABLE IF EXISTS `wishlists`;

CREATE TABLE `wishlists` (
  `wishlist_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`wishlist_id`),
  UNIQUE KEY `user_product_unique` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `wishlists_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `wishlists` */

LOCK TABLES `wishlists` WRITE;

insert  into `wishlists`(`wishlist_id`,`user_id`,`product_id`,`created_at`) values (2,2,6,'2025-02-14 20:39:36'),(4,3,7,'2025-02-15 07:27:37');

UNLOCK TABLES;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
