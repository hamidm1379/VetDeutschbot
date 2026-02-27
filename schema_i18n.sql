-- Database schema for Telegram Language Learning Bot (i18n-ready)
-- MySQL 5.7+ / MariaDB 10.3+
-- This schema uses JSON columns for multilingual content, making it easy to add new languages

-- Create database (uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE telegram_bot;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) DEFAULT NULL COMMENT 'User full name',
    mobile VARCHAR(20) DEFAULT NULL COMMENT 'User mobile number',
    language VARCHAR(10) DEFAULT NULL COMMENT 'Language code (e.g., fa, de, en)',
    current_step INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    account_expires_at DATETIME DEFAULT NULL COMMENT 'Subscription/account expiration',
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_current_step (current_step)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Steps table (i18n-ready with JSON)
CREATE TABLE IF NOT EXISTS steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title_json JSON NOT NULL COMMENT 'JSON object: {"fa": "...", "de": "...", "en": "..."}',
    description_json JSON DEFAULT NULL COMMENT 'JSON object: {"fa": "...", "de": "...", "en": "..."}',
    file_id VARCHAR(255) DEFAULT NULL COMMENT 'Telegram file_id',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Exams table
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    step_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
    UNIQUE KEY unique_step_exam (step_id),
    INDEX idx_step_id (step_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Questions table (i18n-ready with JSON)
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_json JSON NOT NULL COMMENT 'JSON object: {"fa": "...", "de": "...", "en": "..."}',
    options_json TEXT NOT NULL COMMENT 'JSON array of options (language-agnostic)',
    correct_option INT NOT NULL COMMENT '0-based index of correct option',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    INDEX idx_exam_id (exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User exam results table
CREATE TABLE IF NOT EXISTS user_exam_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    step_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL COMMENT 'Score percentage',
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_step_result (user_id, step_id),
    INDEX idx_user_id (user_id),
    INDEX idx_step_id (step_id),
    INDEX idx_passed (passed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migration script to convert old schema to new i18n schema
-- Run this if you have existing data with the old schema

-- ALTER TABLE users MODIFY language VARCHAR(10) DEFAULT NULL;
-- 
-- ALTER TABLE steps 
--     ADD COLUMN title_json JSON,
--     ADD COLUMN description_json JSON;
-- 
-- UPDATE steps SET 
--     title_json = JSON_OBJECT('fa', title_fa, 'de', title_de),
--     description_json = JSON_OBJECT('fa', description_fa, 'de', description_de);
-- 
-- ALTER TABLE steps 
--     DROP COLUMN title_fa,
--     DROP COLUMN title_de,
--     DROP COLUMN description_fa,
--     DROP COLUMN description_de;
-- 
-- ALTER TABLE questions 
--     ADD COLUMN question_json JSON;
-- 
-- UPDATE questions SET 
--     question_json = JSON_OBJECT('fa', question_fa, 'de', question_de);
-- 
-- ALTER TABLE questions 
--     DROP COLUMN question_fa,
--     DROP COLUMN question_de;
