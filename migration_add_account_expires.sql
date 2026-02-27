-- Migration script to add account_expires_at field to users table
-- Run this to add account expiration tracking

ALTER TABLE users 
    ADD COLUMN account_expires_at DATETIME DEFAULT NULL COMMENT 'Account expiration date and time' AFTER mobile;
