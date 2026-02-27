-- Database schema for Telegram Language Learning Bot
-- MySQL 5.7+ / MariaDB 10.3+

-- Create database (uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE telegram_bot;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    language VARCHAR(2) DEFAULT NULL COMMENT 'fa or de',
    current_step INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_current_step (current_step)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Steps table
CREATE TABLE IF NOT EXISTS steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title_fa VARCHAR(255) NOT NULL COMMENT 'Title in Persian',
    title_de VARCHAR(255) NOT NULL COMMENT 'Title in German',
    description_fa TEXT COMMENT 'Description in Persian',
    description_de TEXT COMMENT 'Description in German',
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

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_fa TEXT NOT NULL COMMENT 'Question text in Persian',
    question_de TEXT NOT NULL COMMENT 'Question text in German',
    options_json TEXT NOT NULL COMMENT 'JSON array of options',
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
