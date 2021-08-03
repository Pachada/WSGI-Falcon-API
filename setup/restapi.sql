-- MySQL dump 10.13  Distrib 8.0.22, for Linux (x86_64)
--
-- Host: localhost    Database: restapi
-- ------------------------------------------------------
-- Server version	8.0.26-0ubuntu0.20.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` varchar(300) NOT NULL,
  `user_id` bigint NOT NULL,
  `token` varchar(100) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_device_user_id_idx` (`user_id`),
  CONSTRAINT `fk_device_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES (1,'12345-6789-09876-54321',1,NULL,'2021-05-03 16:06:01','2021-05-03 16:06:01',1),(2,'unknown',1,NULL,'2021-05-04 17:13:40','2021-05-04 17:13:40',1);
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_pool`
--

DROP TABLE IF EXISTS `email_pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_pool` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `send_attemps` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status_id` bigint NOT NULL,
  `template_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailpool_idTemplate_idx` (`template_id`),
  KEY `emailpool_idStatus_idx` (`status_id`),
  CONSTRAINT `fk_email_pool_email_template_id` FOREIGN KEY (`template_id`) REFERENCES `email_template` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_email_pool_status_id` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_pool`
--

LOCK TABLES `email_pool` WRITE;
/*!40000 ALTER TABLE `email_pool` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_pool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_sent`
--

DROP TABLE IF EXISTS `email_sent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_sent` (
  `id` bigint NOT NULL,
  `email` varchar(100) NOT NULL,
  `code` varchar(45) NOT NULL,
  `content` text NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `template_id` bigint NOT NULL,
  `status_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_email_sent_email_template_id_idx` (`template_id`),
  KEY `fk_email_sent_status_id_idx` (`status_id`),
  CONSTRAINT `fk_email_sent_email_template_id` FOREIGN KEY (`template_id`) REFERENCES `email_template` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_email_sent_status_id` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_sent`
--

LOCK TABLES `email_sent` WRITE;
/*!40000 ALTER TABLE `email_sent` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_sent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_template`
--

DROP TABLE IF EXISTS `email_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_template` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `html` text NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_template`
--

LOCK TABLES `email_template` WRITE;
/*!40000 ALTER TABLE `email_template` DISABLE KEYS */;
INSERT INTO `email_template` VALUES (1,'password recovery','Recupera tu contraseña','Correo que envía la otp para recuperar la contraseña','<!doctype html>\n<html xmlns=\'http://www.w3.org/1999/xhtml\' xmlns:v=\'urn:schemas-microsoft-com:vml\' xmlns:o=\'urn:schemas-microsoft-com:office:office\'>\n    <head>\n        <!-- NAME: 1 COLUMN -->\n        <!--[if gte mso 15]>\n        <xml>\n            <o:OfficeDocumentSettings>\n            <o:AllowPNG/>\n            <o:PixelsPerInch>96</o:PixelsPerInch>\n            </o:OfficeDocumentSettings>\n        </xml>\n        <![endif]-->\n        <meta charset=\'UTF-8\'>\n        <meta http-equiv=\'X-UA-Compatible\' content=\'IE=edge\'>\n        <meta name=\'viewport\' content=\'width=device-width, initial-scale=1\'>\n        <title>*|MC:SUBJECT|*</title>\n        \n    <style type=\'text/css\'>\n		p{\n			margin:10px 0;\n			padding:0;\n		}\n		table{\n			border-collapse:collapse;\n		}\n		h1,h2,h3,h4,h5,h6{\n			display:block;\n			margin:0;\n			padding:0;\n		}\n		img,a img{\n			border:0;\n			height:auto;\n			outline:none;\n			text-decoration:none;\n		}\n		body,#bodyTable,#bodyCell{\n			height:100%;\n			margin:0;\n			padding:0;\n			width:100%;\n		}\n		.mcnPreviewText{\n			display:none !important;\n		}\n		#outlook a{\n			padding:0;\n		}\n		img{\n			-ms-interpolation-mode:bicubic;\n		}\n		table{\n			mso-table-lspace:0pt;\n			mso-table-rspace:0pt;\n		}\n		.ReadMsgBody{\n			width:100%;\n		}\n		.ExternalClass{\n			width:100%;\n		}\n		p,a,li,td,blockquote{\n			mso-line-height-rule:exactly;\n		}\n		a[href^=tel],a[href^=sms]{\n			color:inherit;\n			cursor:default;\n			text-decoration:none;\n		}\n		p,a,li,td,body,table,blockquote{\n			-ms-text-size-adjust:100%;\n			-webkit-text-size-adjust:100%;\n		}\n		.ExternalClass,.ExternalClass p,.ExternalClass td,.ExternalClass div,.ExternalClass span,.ExternalClass font{\n			line-height:100%;\n		}\n		a[x-apple-data-detectors]{\n			color:inherit !important;\n			text-decoration:none !important;\n			font-size:inherit !important;\n			font-family:inherit !important;\n			font-weight:inherit !important;\n			line-height:inherit !important;\n		}\n		#bodyCell{\n			padding:10px;\n		}\n		.templateContainer{\n			max-width:600px !important;\n		}\n		a.mcnButton{\n			display:block;\n		}\n		.mcnImage,.mcnRetinaImage{\n			vertical-align:bottom;\n		}\n		.mcnTextContent{\n			word-break:break-word;\n		}\n		.mcnTextContent img{\n			height:auto !important;\n		}\n		.mcnDividerBlock{\n			table-layout:fixed !important;\n		}\n	/*\n	@tab Page\n	@section Background Style\n	@tip Set the background color and top border for your email. You may want to choose colors that match your company\'s branding.\n	*/\n		body,#bodyTable{\n			/*@editable*/background-color:#f5f5f5;\n		}\n	/*\n	@tab Page\n	@section Background Style\n	@tip Set the background color and top border for your email. You may want to choose colors that match your company\'s branding.\n	*/\n		#bodyCell{\n			/*@editable*/border-top:0;\n		}\n	/*\n	@tab Page\n	@section Email Border\n	@tip Set the border for your email.\n	*/\n		.templateContainer{\n			/*@editable*/border:0;\n		}\n	/*\n	@tab Page\n	@section Heading 1\n	@tip Set the styling for all first-level headings in your emails. These should be the largest of your headings.\n	@style heading 1\n	*/\n		h1{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:26px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 2\n	@tip Set the styling for all second-level headings in your emails.\n	@style heading 2\n	*/\n		h2{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:22px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 3\n	@tip Set the styling for all third-level headings in your emails.\n	@style heading 3\n	*/\n		h3{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:20px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 4\n	@tip Set the styling for all fourth-level headings in your emails. These should be the smallest of your headings.\n	@style heading 4\n	*/\n		h4{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:18px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Style\n	@tip Set the background color and borders for your email\'s preheader area.\n	*/\n		#templatePreheader{\n			/*@editable*/background-color:#fafafa;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Text\n	@tip Set the styling for your email\'s preheader text. Choose a size and color that is easy to read.\n	*/\n		#templatePreheader .mcnTextContent,#templatePreheader .mcnTextContent p{\n			/*@editable*/color:#656565;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:12px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Link\n	@tip Set the styling for your email\'s preheader links. Choose a color that helps them stand out from your text.\n	*/\n		#templatePreheader .mcnTextContent a,#templatePreheader .mcnTextContent p a{\n			/*@editable*/color:#656565;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Header\n	@section Header Style\n	@tip Set the background color and borders for your email\'s header area.\n	*/\n		#templateHeader{\n			/*@editable*/background-color:#ffffff;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Header\n	@section Header Text\n	@tip Set the styling for your email\'s header text. Choose a size and color that is easy to read.\n	*/\n		#templateHeader .mcnTextContent,#templateHeader .mcnTextContent p{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:16px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Header\n	@section Header Link\n	@tip Set the styling for your email\'s header links. Choose a color that helps them stand out from your text.\n	*/\n		#templateHeader .mcnTextContent a,#templateHeader .mcnTextContent p a{\n			/*@editable*/color:#007C89;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Body\n	@section Body Style\n	@tip Set the background color and borders for your email\'s body area.\n	*/\n		#templateBody{\n			/*@editable*/background-color:#ffffff;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:2px solid #EAEAEA;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Body\n	@section Body Text\n	@tip Set the styling for your email\'s body text. Choose a size and color that is easy to read.\n	*/\n		#templateBody .mcnTextContent,#templateBody .mcnTextContent p{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:16px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Body\n	@section Body Link\n	@tip Set the styling for your email\'s body links. Choose a color that helps them stand out from your text.\n	*/\n		#templateBody .mcnTextContent a,#templateBody .mcnTextContent p a{\n			/*@editable*/color:#ff7643;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Footer\n	@section Footer Style\n	@tip Set the background color and borders for your email\'s footer area.\n	*/\n		#templateFooter{\n			/*@editable*/background-color:#ff7643;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:9px;\n		}\n	/*\n	@tab Footer\n	@section Footer Text\n	@tip Set the styling for your email\'s footer text. Choose a size and color that is easy to read.\n	*/\n		#templateFooter .mcnTextContent,#templateFooter .mcnTextContent p{\n			/*@editable*/color:#656565;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:12px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:center;\n		}\n	/*\n	@tab Footer\n	@section Footer Link\n	@tip Set the styling for your email\'s footer links. Choose a color that helps them stand out from your text.\n	*/\n		#templateFooter .mcnTextContent a,#templateFooter .mcnTextContent p a{\n			/*@editable*/color:#ffffff;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	@media only screen and (min-width:768px){\n		.templateContainer{\n			width:600px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		body,table,td,p,a,li,blockquote{\n			-webkit-text-size-adjust:none !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		body{\n			width:100% !important;\n			min-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnRetinaImage{\n			max-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImage{\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnCartContainer,.mcnCaptionTopContent,.mcnRecContentContainer,.mcnCaptionBottomContent,.mcnTextContentContainer,.mcnBoxedTextContentContainer,.mcnImageGroupContentContainer,.mcnCaptionLeftTextContentContainer,.mcnCaptionRightTextContentContainer,.mcnCaptionLeftImageContentContainer,.mcnCaptionRightImageContentContainer,.mcnImageCardLeftTextContentContainer,.mcnImageCardRightTextContentContainer,.mcnImageCardLeftImageContentContainer,.mcnImageCardRightImageContentContainer{\n			max-width:100% !important;\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnBoxedTextContentContainer{\n			min-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupContent{\n			padding:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnCaptionLeftContentOuter .mcnTextContent,.mcnCaptionRightContentOuter .mcnTextContent{\n			padding-top:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardTopImageContent,.mcnCaptionBottomContent:last-child .mcnCaptionBottomImageContent,.mcnCaptionBlockInner .mcnCaptionTopContent:last-child .mcnTextContent{\n			padding-top:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardBottomImageContent{\n			padding-bottom:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupBlockInner{\n			padding-top:0 !important;\n			padding-bottom:0 !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupBlockOuter{\n			padding-top:9px !important;\n			padding-bottom:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnTextContent,.mcnBoxedTextContentColumn{\n			padding-right:18px !important;\n			padding-left:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardLeftImageContent,.mcnImageCardRightImageContent{\n			padding-right:18px !important;\n			padding-bottom:0 !important;\n			padding-left:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcpreview-image-uploader{\n			display:none !important;\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 1\n	@tip Make the first-level headings larger in size for better readability on small screens.\n	*/\n		h1{\n			/*@editable*/font-size:22px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 2\n	@tip Make the second-level headings larger in size for better readability on small screens.\n	*/\n		h2{\n			/*@editable*/font-size:20px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 3\n	@tip Make the third-level headings larger in size for better readability on small screens.\n	*/\n		h3{\n			/*@editable*/font-size:18px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 4\n	@tip Make the fourth-level headings larger in size for better readability on small screens.\n	*/\n		h4{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Boxed Text\n	@tip Make the boxed text larger in size for better readability on small screens. We recommend a font size of at least 16px.\n	*/\n		.mcnBoxedTextContentContainer .mcnTextContent,.mcnBoxedTextContentContainer .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Preheader Visibility\n	@tip Set the visibility of the email\'s preheader on small screens. You can hide it to save space.\n	*/\n		#templatePreheader{\n			/*@editable*/display:block !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Preheader Text\n	@tip Make the preheader text larger in size for better readability on small screens.\n	*/\n		#templatePreheader .mcnTextContent,#templatePreheader .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Header Text\n	@tip Make the header text larger in size for better readability on small screens.\n	*/\n		#templateHeader .mcnTextContent,#templateHeader .mcnTextContent p{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Body Text\n	@tip Make the body text larger in size for better readability on small screens. We recommend a font size of at least 16px.\n	*/\n		#templateBody .mcnTextContent,#templateBody .mcnTextContent p{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Footer Text\n	@tip Make the footer content text larger in size for better readability on small screens.\n	*/\n		#templateFooter .mcnTextContent,#templateFooter .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}</style></head>\n    <body>\n        <!--*|IF:MC_PREVIEW_TEXT|*-->\n        <!--[if !gte mso 9]><!----><span class=\'mcnPreviewText\' style=\'display:none; font-size:0px; line-height:0px; max-height:0px; max-width:0px; opacity:0; overflow:hidden; visibility:hidden; mso-hide:all;\'>*|MC_PREVIEW_TEXT|*</span><!--<![endif]-->\n        <!--*|END:IF|*-->\n        <center>\n            <table align=\'center\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' height=\'100%\' width=\'100%\' id=\'bodyTable\'>\n                <tr>\n                    <td align=\'center\' valign=\'top\' id=\'bodyCell\'>\n                        <!-- BEGIN TEMPLATE // -->\n                        <!--[if (gte mso 9)|(IE)]>\n                        <table align=\'center\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'600\' style=\'width:600px;\'>\n                        <tr>\n                        <td align=\'center\' valign=\'top\' width=\'600\' style=\'width:600px;\'>\n                        <![endif]-->\n                        <table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'templateContainer\'>\n                            <tr>\n                                <td valign=\'top\' id=\'templatePreheader\'></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateHeader\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnImageBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnImageBlockOuter\'>\n            <tr>\n                <td valign=\'top\' style=\'padding:0px\' class=\'mcnImageBlockInner\'>\n                    <table align=\'left\' width=\'100%\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' class=\'mcnImageContentContainer\' style=\'min-width:100%;\'>\n                        <tbody><tr>\n                            <td class=\'mcnImageContent\' valign=\'top\' style=\'padding-right: 0px; padding-left: 0px; padding-top: 0; padding-bottom: 0; text-align:center;\'>\n                                \n                                    \n                                        <img align=\'center\' alt=\'\' src=\'https://lh3.googleusercontent.com/VV3nomfXajfiE1otT-5NfsEV_Eu2vC1jqpEVB-E61bTsaIdAUvizGGYnY0EDimDiOkTlAYhe0ykap7-JD4UMcTwHnFmM-D8LysgEzTmBs4STKg8jXjG1DrdwZzOJ8Hop8fFkbpG7FPreaBPDlWljEEfkqc1tIqApled4XY1jNc-wEj1UYEgfzPZ3BOdaa07o-e6hqmZH04z6xrirUV-Preq87Xkmtd72ZC4Ms7omLy0eE5kySapqzT55vRxH--qPfGIJrzg1dzU8kcITOlxTvGSl849B6RXsYSDA6XHM-JWH8TYVQ19FbSjI9VFcwY96E8iVwJHBdQXsiARMQikM65-PNldJGq7p6HicTQS-rveC0C3DFxU49fmfzA9ybVAe9A1keF4RZUH3O74ea0sIl7Pi6dlM1nySiDkPu9X9uNDDVoEBv2pyyDDRxaAxF7xT5_LlepEzpyWPj5__BijrQz5q9pEhB2-CD3fItvXfIhnk__ClBmc4Ltok_P47L7REf5mJrJGNojoNAa7VL46CZa4ROgeYnusudLC0UO-bOHoFz6Lh_GN-AeszbhAdDO8TvXdTG69FMR5o6ny3j2eHYGDlw0QpOpyGsjKZ6nRDMZcgKwUnhJzQTzXhSduVsOgO7TmxN_6qMwBUFvQN87qCZ_S3vMVwJZK0mdbNoickIRoWkIwU9SwMvP0O24IoPD9Xx9ZzcHPh0sKmRwuhz6h9QMvA=w1544-h952-no?authuser=1\' width=\'599.9999389648438\' style=\'max-width: 2899px; padding-bottom: 0px; vertical-align: bottom; display: inline !important; border-top-left-radius: 0%; border-top-right-radius: 0%; border-bottom-right-radius: 0%; border-bottom-left-radius: 0%;\' class=\'mcnImage\'>\n                                    \n                                \n                            </td>\n                        </tr>\n                    </tbody></table>\n                </td>\n            </tr>\n    </tbody>\n</table><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;\'>\n                        \n                            <div style=\'text-align: left;\'>&nbsp;</div>\n\n<div style=\'text-align: center;\'><br>\n<span style=\'font-family:arial,helvetica neue,helvetica,sans-serif\'><span style=\'font-size:20px\'>Recibimos una solicitud para cambiar tu contraseña.<br>\n<br>\nUsa el siguiente código para hacerlo:</span></span></div>\n\n<div style=\'text-align: center;\'>&nbsp;</div>\n\n<div style=\'text-align: center;\'><span style=\'color:#FF7643\'><span style=\'font-size:20px\'><strong>{{otp}}</strong></span></span><br>\n&nbsp;</div>\n\n<div style=\'text-align: center;\'><span style=\'font-size:20px\'>Si no solicitaste éste cambio has caso omiso a este correo.</span><br>\n&nbsp;</div>\n\n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnDividerBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnDividerBlockOuter\'>\n        <tr>\n            <td class=\'mcnDividerBlockInner\' style=\'min-width: 100%; padding: 18px;\'>\n                <table class=\'mcnDividerContent\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' style=\'min-width: 100%;border-top-width: 2px;border-top-style: solid;border-top-color: #EAEAEA;\'>\n                    <tbody><tr>\n                        <td>\n                            <span></span>\n                        </td>\n                    </tr>\n                </tbody></table>\n<!--            \n                <td class=\'mcnDividerBlockInner\' style=\'padding: 18px;\'>\n                <hr class=\'mcnDividerContent\' style=\'border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;\' />\n-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateBody\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding: 0px 18px 9px; line-height: 100%;\'>\n                        \n                            <span style=\'font-size:10px\'>Aviso de Privacidad. Este mensaje y cualquier archivo anexo incluido en el mismo (en lo sucesivo la “Información”) son enviados únicamente para el destinatario previsto y pueden contener información confidencial y/o privilegiada. Si usted no es el destinatario previsto, por este medio se le notifica que cualquier copia, uso, o distribución de la Información se encuentra estrictamente prohibida y sujeta a las sanciones establecidas en las leyes correspondientes por lo que deberá notificarnos por E-mail y suprimir inmediatamente este mensaje de su sistema.</span>\n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateFooter\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;\'>\n                        \n                            \n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                        </table>\n                        <!--[if (gte mso 9)|(IE)]>\n                        </td>\n                        </tr>\n                        </table>\n                        <![endif]-->\n                        <!-- // END TEMPLATE -->\n                    </td>\n                </tr>\n            </table>\n        </center>\n    </body>\n</html>','2021-04-22 19:35:36','2021-04-22 19:35:36',1),(2,'email confirmation','Confirma tu correo','Correo con el código para verificar una dirección email','<!doctype html>\n<html xmlns=\'http://www.w3.org/1999/xhtml\' xmlns:v=\'urn:schemas-microsoft-com:vml\' xmlns:o=\'urn:schemas-microsoft-com:office:office\'>\n    <head>\n        <!-- NAME: 1 COLUMN -->\n        <!--[if gte mso 15]>\n        <xml>\n            <o:OfficeDocumentSettings>\n            <o:AllowPNG/>\n            <o:PixelsPerInch>96</o:PixelsPerInch>\n            </o:OfficeDocumentSettings>\n        </xml>\n        <![endif]-->\n        <meta charset=\'UTF-8\'>\n        <meta http-equiv=\'X-UA-Compatible\' content=\'IE=edge\'>\n        <meta name=\'viewport\' content=\'width=device-width, initial-scale=1\'>\n        <title>*|MC:SUBJECT|*</title>\n        \n    <style type=\'text/css\'>\n		p{\n			margin:10px 0;\n			padding:0;\n		}\n		table{\n			border-collapse:collapse;\n		}\n		h1,h2,h3,h4,h5,h6{\n			display:block;\n			margin:0;\n			padding:0;\n		}\n		img,a img{\n			border:0;\n			height:auto;\n			outline:none;\n			text-decoration:none;\n		}\n		body,#bodyTable,#bodyCell{\n			height:100%;\n			margin:0;\n			padding:0;\n			width:100%;\n		}\n		.mcnPreviewText{\n			display:none !important;\n		}\n		#outlook a{\n			padding:0;\n		}\n		img{\n			-ms-interpolation-mode:bicubic;\n		}\n		table{\n			mso-table-lspace:0pt;\n			mso-table-rspace:0pt;\n		}\n		.ReadMsgBody{\n			width:100%;\n		}\n		.ExternalClass{\n			width:100%;\n		}\n		p,a,li,td,blockquote{\n			mso-line-height-rule:exactly;\n		}\n		a[href^=tel],a[href^=sms]{\n			color:inherit;\n			cursor:default;\n			text-decoration:none;\n		}\n		p,a,li,td,body,table,blockquote{\n			-ms-text-size-adjust:100%;\n			-webkit-text-size-adjust:100%;\n		}\n		.ExternalClass,.ExternalClass p,.ExternalClass td,.ExternalClass div,.ExternalClass span,.ExternalClass font{\n			line-height:100%;\n		}\n		a[x-apple-data-detectors]{\n			color:inherit !important;\n			text-decoration:none !important;\n			font-size:inherit !important;\n			font-family:inherit !important;\n			font-weight:inherit !important;\n			line-height:inherit !important;\n		}\n		#bodyCell{\n			padding:10px;\n		}\n		.templateContainer{\n			max-width:600px !important;\n		}\n		a.mcnButton{\n			display:block;\n		}\n		.mcnImage,.mcnRetinaImage{\n			vertical-align:bottom;\n		}\n		.mcnTextContent{\n			word-break:break-word;\n		}\n		.mcnTextContent img{\n			height:auto !important;\n		}\n		.mcnDividerBlock{\n			table-layout:fixed !important;\n		}\n	/*\n	@tab Page\n	@section Background Style\n	@tip Set the background color and top border for your email. You may want to choose colors that match your company\'s branding.\n	*/\n		body,#bodyTable{\n			/*@editable*/background-color:#f5f5f5;\n		}\n	/*\n	@tab Page\n	@section Background Style\n	@tip Set the background color and top border for your email. You may want to choose colors that match your company\'s branding.\n	*/\n		#bodyCell{\n			/*@editable*/border-top:0;\n		}\n	/*\n	@tab Page\n	@section Email Border\n	@tip Set the border for your email.\n	*/\n		.templateContainer{\n			/*@editable*/border:0;\n		}\n	/*\n	@tab Page\n	@section Heading 1\n	@tip Set the styling for all first-level headings in your emails. These should be the largest of your headings.\n	@style heading 1\n	*/\n		h1{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:26px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 2\n	@tip Set the styling for all second-level headings in your emails.\n	@style heading 2\n	*/\n		h2{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:22px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 3\n	@tip Set the styling for all third-level headings in your emails.\n	@style heading 3\n	*/\n		h3{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:20px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Page\n	@section Heading 4\n	@tip Set the styling for all fourth-level headings in your emails. These should be the smallest of your headings.\n	@style heading 4\n	*/\n		h4{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:18px;\n			/*@editable*/font-style:normal;\n			/*@editable*/font-weight:bold;\n			/*@editable*/line-height:125%;\n			/*@editable*/letter-spacing:normal;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Style\n	@tip Set the background color and borders for your email\'s preheader area.\n	*/\n		#templatePreheader{\n			/*@editable*/background-color:#fafafa;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Text\n	@tip Set the styling for your email\'s preheader text. Choose a size and color that is easy to read.\n	*/\n		#templatePreheader .mcnTextContent,#templatePreheader .mcnTextContent p{\n			/*@editable*/color:#656565;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:12px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Preheader\n	@section Preheader Link\n	@tip Set the styling for your email\'s preheader links. Choose a color that helps them stand out from your text.\n	*/\n		#templatePreheader .mcnTextContent a,#templatePreheader .mcnTextContent p a{\n			/*@editable*/color:#656565;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Header\n	@section Header Style\n	@tip Set the background color and borders for your email\'s header area.\n	*/\n		#templateHeader{\n			/*@editable*/background-color:#ffffff;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Header\n	@section Header Text\n	@tip Set the styling for your email\'s header text. Choose a size and color that is easy to read.\n	*/\n		#templateHeader .mcnTextContent,#templateHeader .mcnTextContent p{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:16px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Header\n	@section Header Link\n	@tip Set the styling for your email\'s header links. Choose a color that helps them stand out from your text.\n	*/\n		#templateHeader .mcnTextContent a,#templateHeader .mcnTextContent p a{\n			/*@editable*/color:#007C89;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Body\n	@section Body Style\n	@tip Set the background color and borders for your email\'s body area.\n	*/\n		#templateBody{\n			/*@editable*/background-color:#ffffff;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:2px solid #EAEAEA;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:0px;\n		}\n	/*\n	@tab Body\n	@section Body Text\n	@tip Set the styling for your email\'s body text. Choose a size and color that is easy to read.\n	*/\n		#templateBody .mcnTextContent,#templateBody .mcnTextContent p{\n			/*@editable*/color:#202020;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:16px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:left;\n		}\n	/*\n	@tab Body\n	@section Body Link\n	@tip Set the styling for your email\'s body links. Choose a color that helps them stand out from your text.\n	*/\n		#templateBody .mcnTextContent a,#templateBody .mcnTextContent p a{\n			/*@editable*/color:#ff7643;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	/*\n	@tab Footer\n	@section Footer Style\n	@tip Set the background color and borders for your email\'s footer area.\n	*/\n		#templateFooter{\n			/*@editable*/background-color:#ff7643;\n			/*@editable*/background-image:none;\n			/*@editable*/background-repeat:no-repeat;\n			/*@editable*/background-position:center;\n			/*@editable*/background-size:cover;\n			/*@editable*/border-top:0;\n			/*@editable*/border-bottom:0;\n			/*@editable*/padding-top:0px;\n			/*@editable*/padding-bottom:9px;\n		}\n	/*\n	@tab Footer\n	@section Footer Text\n	@tip Set the styling for your email\'s footer text. Choose a size and color that is easy to read.\n	*/\n		#templateFooter .mcnTextContent,#templateFooter .mcnTextContent p{\n			/*@editable*/color:#656565;\n			/*@editable*/font-family:Helvetica;\n			/*@editable*/font-size:12px;\n			/*@editable*/line-height:150%;\n			/*@editable*/text-align:center;\n		}\n	/*\n	@tab Footer\n	@section Footer Link\n	@tip Set the styling for your email\'s footer links. Choose a color that helps them stand out from your text.\n	*/\n		#templateFooter .mcnTextContent a,#templateFooter .mcnTextContent p a{\n			/*@editable*/color:#ffffff;\n			/*@editable*/font-weight:normal;\n			/*@editable*/text-decoration:underline;\n		}\n	@media only screen and (min-width:768px){\n		.templateContainer{\n			width:600px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		body,table,td,p,a,li,blockquote{\n			-webkit-text-size-adjust:none !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		body{\n			width:100% !important;\n			min-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnRetinaImage{\n			max-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImage{\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnCartContainer,.mcnCaptionTopContent,.mcnRecContentContainer,.mcnCaptionBottomContent,.mcnTextContentContainer,.mcnBoxedTextContentContainer,.mcnImageGroupContentContainer,.mcnCaptionLeftTextContentContainer,.mcnCaptionRightTextContentContainer,.mcnCaptionLeftImageContentContainer,.mcnCaptionRightImageContentContainer,.mcnImageCardLeftTextContentContainer,.mcnImageCardRightTextContentContainer,.mcnImageCardLeftImageContentContainer,.mcnImageCardRightImageContentContainer{\n			max-width:100% !important;\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnBoxedTextContentContainer{\n			min-width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupContent{\n			padding:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnCaptionLeftContentOuter .mcnTextContent,.mcnCaptionRightContentOuter .mcnTextContent{\n			padding-top:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardTopImageContent,.mcnCaptionBottomContent:last-child .mcnCaptionBottomImageContent,.mcnCaptionBlockInner .mcnCaptionTopContent:last-child .mcnTextContent{\n			padding-top:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardBottomImageContent{\n			padding-bottom:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupBlockInner{\n			padding-top:0 !important;\n			padding-bottom:0 !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageGroupBlockOuter{\n			padding-top:9px !important;\n			padding-bottom:9px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnTextContent,.mcnBoxedTextContentColumn{\n			padding-right:18px !important;\n			padding-left:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcnImageCardLeftImageContent,.mcnImageCardRightImageContent{\n			padding-right:18px !important;\n			padding-bottom:0 !important;\n			padding-left:18px !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n		.mcpreview-image-uploader{\n			display:none !important;\n			width:100% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 1\n	@tip Make the first-level headings larger in size for better readability on small screens.\n	*/\n		h1{\n			/*@editable*/font-size:22px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 2\n	@tip Make the second-level headings larger in size for better readability on small screens.\n	*/\n		h2{\n			/*@editable*/font-size:20px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 3\n	@tip Make the third-level headings larger in size for better readability on small screens.\n	*/\n		h3{\n			/*@editable*/font-size:18px !important;\n			/*@editable*/line-height:125% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Heading 4\n	@tip Make the fourth-level headings larger in size for better readability on small screens.\n	*/\n		h4{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Boxed Text\n	@tip Make the boxed text larger in size for better readability on small screens. We recommend a font size of at least 16px.\n	*/\n		.mcnBoxedTextContentContainer .mcnTextContent,.mcnBoxedTextContentContainer .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Preheader Visibility\n	@tip Set the visibility of the email\'s preheader on small screens. You can hide it to save space.\n	*/\n		#templatePreheader{\n			/*@editable*/display:block !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Preheader Text\n	@tip Make the preheader text larger in size for better readability on small screens.\n	*/\n		#templatePreheader .mcnTextContent,#templatePreheader .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Header Text\n	@tip Make the header text larger in size for better readability on small screens.\n	*/\n		#templateHeader .mcnTextContent,#templateHeader .mcnTextContent p{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Body Text\n	@tip Make the body text larger in size for better readability on small screens. We recommend a font size of at least 16px.\n	*/\n		#templateBody .mcnTextContent,#templateBody .mcnTextContent p{\n			/*@editable*/font-size:16px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}	@media only screen and (max-width: 480px){\n	/*\n	@tab Mobile Styles\n	@section Footer Text\n	@tip Make the footer content text larger in size for better readability on small screens.\n	*/\n		#templateFooter .mcnTextContent,#templateFooter .mcnTextContent p{\n			/*@editable*/font-size:14px !important;\n			/*@editable*/line-height:150% !important;\n		}\n\n}</style></head>\n    <body>\n        <!--*|IF:MC_PREVIEW_TEXT|*-->\n        <!--[if !gte mso 9]><!----><span class=\'mcnPreviewText\' style=\'display:none; font-size:0px; line-height:0px; max-height:0px; max-width:0px; opacity:0; overflow:hidden; visibility:hidden; mso-hide:all;\'>*|MC_PREVIEW_TEXT|*</span><!--<![endif]-->\n        <!--*|END:IF|*-->\n        <center>\n            <table align=\'center\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' height=\'100%\' width=\'100%\' id=\'bodyTable\'>\n                <tr>\n                    <td align=\'center\' valign=\'top\' id=\'bodyCell\'>\n                        <!-- BEGIN TEMPLATE // -->\n                        <!--[if (gte mso 9)|(IE)]>\n                        <table align=\'center\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'600\' style=\'width:600px;\'>\n                        <tr>\n                        <td align=\'center\' valign=\'top\' width=\'600\' style=\'width:600px;\'>\n                        <![endif]-->\n                        <table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'templateContainer\'>\n                            <tr>\n                                <td valign=\'top\' id=\'templatePreheader\'></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateHeader\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnImageBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnImageBlockOuter\'>\n            <tr>\n                <td valign=\'top\' style=\'padding:0px\' class=\'mcnImageBlockInner\'>\n                    <table align=\'left\' width=\'100%\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' class=\'mcnImageContentContainer\' style=\'min-width:100%;\'>\n                        <tbody><tr>\n                            <td class=\'mcnImageContent\' valign=\'top\' style=\'padding-right: 0px; padding-left: 0px; padding-top: 0; padding-bottom: 0; text-align:center;\'>\n                                \n                                    \n                                        <img align=\'center\' alt=\'\' src=\'https://lh3.googleusercontent.com/PruwE3I6XeHB3sNR8yAxCVxDcKBazhkBf1gmKb8TLlmL7c3T2OZtXgSOIfNJufbo2Cocg6f8K6_1P0vkHNmi78JANKTqsEHA9k1QgGHp8chXwGznKqpR-dOHFjq4JOu0dvJGdoq7MZBkf-E1u6eJD5KSO1DIUxN5MrUu77ywTA59a4GataPEHPBfBt7HyZ347KflHsYwBVSYW4Z4BE5sD9dppY355mJ7kfkdxGsHuc0RWFDOehgEV1WVwTgbIIhwFtDQ1XBxaEkDTpyAHaFuoGZWfO0nCj8jCVM4CE2Sl0yQuVWwhIpMJgFV8hMQzVjc-ci5TP6QmM0LBSez0vVjLsElbOyoX_t9NQelWTkDiRQpNCPn_bDSSSNBnKoijNdQdo0k8BH1nIDBR8PVsv9ZA2Nuc-WCUNOQIheSqBndVQQZRy6_twOQ-wgyj8vO5wFu-hfjQVKrYY_iAPeeHUJQPGUH2sNRndmnnS8MtffgUT90-dNEW9F22tgOdbCFFwaQz-oy7TkmuWh5Vbay9oTSManES3PLMXm-Goq8RNj3dr5Fv7szCFBMvatg_5kBpb9_gVvwD9RKw9PHnTEYRyEXCJJkCGQVAI6W6oz_NtydpCKPQEN8AkRNMq8eK4X42mrWkj8j0lVeB2R93KuZ6cEwmyVHYm4lOM1U4L2gqsxJ6gNLNiarUVEsnAT7GulyFSFjBjy-69gi00GA2zVFaot4AEjG=w1544-h952-no?authuser=1\' width=\'599.9999389648438\' style=\'max-width: 2899px; padding-bottom: 0px; vertical-align: bottom; display: inline !important; border-top-left-radius: 0%; border-top-right-radius: 0%; border-bottom-right-radius: 0%; border-bottom-left-radius: 0%;\' class=\'mcnImage\'>\n                                    \n                                \n                            </td>\n                        </tr>\n                    </tbody></table>\n                </td>\n            </tr>\n    </tbody>\n</table><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;\'>\n                        \n                            <div style=\'text-align: left;\'>&nbsp;</div>\n\n<div style=\'text-align: center;\'><br>\n<span style=\'font-family:arial,helvetica neue,helvetica,sans-serif\'><span style=\'font-size:20px\'>Hola, confirmar tu correo nos ayuda a proteger tu cuenta.<br>\n<br>\nUsa el siguiente código para hacerlo:</span></span></div>\n\n<div style=\'text-align: center;\'>&nbsp;</div>\n\n<div style=\'text-align: center;\'><span style=\'color:#FF7643\'><span style=\'font-size:20px\'><strong>{{email_confirmation_code}}</strong></span></span><br>\n&nbsp;</div>\n\n<div style=\'text-align: center;\'><span style=\'font-size:20px\'>Si no solicitaste esta confirmación, has caso omiso.</span><br>\n&nbsp;</div>\n\n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnDividerBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnDividerBlockOuter\'>\n        <tr>\n            <td class=\'mcnDividerBlockInner\' style=\'min-width: 100%; padding: 18px;\'>\n                <table class=\'mcnDividerContent\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' style=\'min-width: 100%;border-top-width: 2px;border-top-style: solid;border-top-color: #EAEAEA;\'>\n                    <tbody><tr>\n                        <td>\n                            <span></span>\n                        </td>\n                    </tr>\n                </tbody></table>\n<!--            \n                <td class=\'mcnDividerBlockInner\' style=\'padding: 18px;\'>\n                <hr class=\'mcnDividerContent\' style=\'border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;\' />\n-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateBody\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding: 0px 18px 9px; line-height: 100%;\'>\n                        \n                            <span style=\'font-size:10px\'>Aviso de Privacidad. Este mensaje y cualquier archivo anexo incluido en el mismo (en lo sucesivo la “Información”) son enviados únicamente para el destinatario previsto y pueden contener información confidencial y/o privilegiada. Si usted no es el destinatario previsto, por este medio se le notifica que cualquier copia, uso, o distribución de la Información se encuentra estrictamente prohibida y sujeta a las sanciones establecidas en las leyes correspondientes por lo que deberá notificarnos por E-mail y suprimir inmediatamente este mensaje de su sistema.</span>\n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                            <tr>\n                                <td valign=\'top\' id=\'templateFooter\'><table border=\'0\' cellpadding=\'0\' cellspacing=\'0\' width=\'100%\' class=\'mcnTextBlock\' style=\'min-width:100%;\'>\n    <tbody class=\'mcnTextBlockOuter\'>\n        <tr>\n            <td valign=\'top\' class=\'mcnTextBlockInner\' style=\'padding-top:9px;\'>\n              	<!--[if mso]>\n				<table align=\'left\' border=\'0\' cellspacing=\'0\' cellpadding=\'0\' width=\'100%\' style=\'width:100%;\'>\n				<tr>\n				<![endif]-->\n			    \n				<!--[if mso]>\n				<td valign=\'top\' width=\'599\' style=\'width:599px;\'>\n				<![endif]-->\n                <table align=\'left\' border=\'0\' cellpadding=\'0\' cellspacing=\'0\' style=\'max-width:100%; min-width:100%;\' width=\'100%\' class=\'mcnTextContentContainer\'>\n                    <tbody><tr>\n                        \n                        <td valign=\'top\' class=\'mcnTextContent\' style=\'padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;\'>\n                        \n                            \n                        </td>\n                    </tr>\n                </tbody></table>\n				<!--[if mso]>\n				</td>\n				<![endif]-->\n                \n				<!--[if mso]>\n				</tr>\n				</table>\n				<![endif]-->\n            </td>\n        </tr>\n    </tbody>\n</table></td>\n                            </tr>\n                        </table>\n                        <!--[if (gte mso 9)|(IE)]>\n                        </td>\n                        </tr>\n                        </table>\n                        <![endif]-->\n                        <!-- // END TEMPLATE -->\n                    </td>\n                </tr>\n            </table>\n        </center>\n    </body>\n</html>','2021-05-03 12:06:18','2021-05-03 12:06:18',1);
/*!40000 ALTER TABLE `email_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `file`
--

DROP TABLE IF EXISTS `file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `file` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `object` varchar(255) NOT NULL,
  `size` int NOT NULL,
  `type` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `hash` varchar(255) NOT NULL,
  `is_thumbnail` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file`
--

LOCK TABLES `file` WRITE;
/*!40000 ALTER TABLE `file` DISABLE KEYS */;
/*!40000 ALTER TABLE `file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `id` bigint NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `birthday` datetime DEFAULT NULL,
  `sex` varchar(45) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'Daniel','Trejo','1998-01-10 00:00:00',NULL,'2021-05-03 10:46:20','2021-05-03 10:46:20',1);
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `push_notification_catalogue`
--

DROP TABLE IF EXISTS `push_notification_catalogue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `push_notification_catalogue` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `push_notification_catalogue`
--

LOCK TABLES `push_notification_catalogue` WRITE;
/*!40000 ALTER TABLE `push_notification_catalogue` DISABLE KEYS */;
INSERT INTO `push_notification_catalogue` VALUES (1,'GOTO_USER_PROFILE');
/*!40000 ALTER TABLE `push_notification_catalogue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `push_notification_pool`
--

DROP TABLE IF EXISTS `push_notification_pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `push_notification_pool` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `template_id` bigint NOT NULL,
  `status_id` bigint NOT NULL,
  `notification_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `message` varchar(200) NOT NULL,
  `data` varchar(200) DEFAULT NULL,
  `ticket` varchar(200) DEFAULT NULL,
  `sendattemps` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_push_notification_pool_user_id_idx` (`user_id`),
  KEY `fk_push_notification_pool_push_notification_template_id_idx` (`template_id`),
  KEY `fk_push_notification_pool_status_id_idx` (`status_id`),
  CONSTRAINT `fk_push_notification_pool_push_notification_template_id` FOREIGN KEY (`template_id`) REFERENCES `push_notification_template` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_pool_status_id` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_pool_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `push_notification_pool`
--

LOCK TABLES `push_notification_pool` WRITE;
/*!40000 ALTER TABLE `push_notification_pool` DISABLE KEYS */;
/*!40000 ALTER TABLE `push_notification_pool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `push_notification_sent`
--

DROP TABLE IF EXISTS `push_notification_sent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `push_notification_sent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `device_id` bigint NOT NULL,
  `template_id` bigint NOT NULL,
  `status_id` bigint NOT NULL,
  `push_notification_pool_id` bigint NOT NULL,
  `ticket` varchar(200) DEFAULT NULL,
  `message` varchar(200) NOT NULL,
  `data` varchar(200) NOT NULL,
  `comments` varchar(100) DEFAULT NULL,
  `read` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_push_notification_sent_user_id_idx` (`user_id`),
  KEY `fk_push_notification_sent_devie_id_idx` (`device_id`),
  KEY `fk_push_notification_sent_push_notification_template_id_idx` (`template_id`),
  KEY `fk_push_notification_sent_status_id_idx` (`status_id`),
  KEY `fk_push_notification_sent_push_notification_pool_id_idx` (`push_notification_pool_id`),
  CONSTRAINT `fk_push_notification_sent_device_id` FOREIGN KEY (`device_id`) REFERENCES `device` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_sent_push_notification_pool_id` FOREIGN KEY (`push_notification_pool_id`) REFERENCES `push_notification_pool` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_sent_push_notification_template_id` FOREIGN KEY (`template_id`) REFERENCES `push_notification_template` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_sent_status_id` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_push_notification_sent_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `push_notification_sent`
--

LOCK TABLES `push_notification_sent` WRITE;
/*!40000 ALTER TABLE `push_notification_sent` DISABLE KEYS */;
/*!40000 ALTER TABLE `push_notification_sent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `push_notification_template`
--

DROP TABLE IF EXISTS `push_notification_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `push_notification_template` (
  `id` bigint NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `title` varchar(200) NOT NULL,
  `message` varchar(200) NOT NULL,
  `private` tinyint(1) NOT NULL,
  `catalogue_id` bigint NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_push_notification_template_catalogue_id_idx` (`catalogue_id`),
  CONSTRAINT `fk_push_notification_template_catalogue_id` FOREIGN KEY (`catalogue_id`) REFERENCES `push_notification_catalogue` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `push_notification_template`
--

LOCK TABLES `push_notification_template` WRITE;
/*!40000 ALTER TABLE `push_notification_template` DISABLE KEYS */;
/*!40000 ALTER TABLE `push_notification_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'root','2021-04-22 19:26:51','2021-04-22 19:26:51',1),(2,'user','2021-05-03 16:18:19','2021-05-03 16:18:19',1);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '		',
  `device_id` bigint NOT NULL,
  `token` varchar(120) NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_session_user_id_idx` (`user_id`),
  KEY `fk_session_device_id_idx` (`device_id`),
  CONSTRAINT `fk_session_device_id` FOREIGN KEY (`device_id`) REFERENCES `device` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_session_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session`
--

LOCK TABLES `session` WRITE;
/*!40000 ALTER TABLE `session` DISABLE KEYS */;
INSERT INTO `session` VALUES (1,1,1,'O4FIfN4kUsbJHAaaJCSldp2Fnm_LG2yxU7wzNqboZOs','2021-05-03 16:06:01','2021-08-02 21:44:34',1),(2,1,2,'ha1b2ijiCDf_ah96LNIo0iSNShK_JmQdc9pezOmkpd8','2021-05-04 17:13:40','2021-05-04 17:13:40',1);
/*!40000 ALTER TABLE `session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `status` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `description` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES (1,'pending'),(2,'processing'),(3,'error'),(4,'send');
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(300) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `role_id` bigint NOT NULL,
  `person_id` bigint DEFAULT NULL,
  `otp` varchar(6) DEFAULT NULL,
  `otp_time` datetime DEFAULT NULL,
  `email_confirmation_code` varchar(6) DEFAULT NULL,
  `email_confirmation_code_time` datetime DEFAULT NULL,
  `confirmed_email` tinyint(1) DEFAULT '0',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enable` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_user_role_id_idx` (`role_id`),
  KEY `fk_user_person_id_idx` (`person_id`),
  CONSTRAINT `fk_user_person_id` FOREIGN KEY (`person_id`) REFERENCES `person` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_role_id` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'daniel.trejo','a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3','dtrejog98@gmail.com','5528461145',1,1,NULL,NULL,NULL,NULL,0,'2021-05-03 16:05:35','2021-05-04 17:24:50',1);
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

-- Dump completed on 2021-08-03 10:52:08
