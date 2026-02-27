-- Migration script to add name and mobile fields to users table
-- Run this if you have existing data

ALTER TABLE users 
    ADD COLUMN name VARCHAR(255) DEFAULT NULL COMMENT 'User full name' AFTER telegram_id,
    ADD COLUMN mobile VARCHAR(20) DEFAULT NULL COMMENT 'User mobile number' AFTER name;
