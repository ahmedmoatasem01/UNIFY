-- Migration: Add Is_Read column to Message table
-- Run this script to update existing database schema for messaging feature

USE unify;

-- Add Is_Read column
ALTER TABLE Message ADD COLUMN Is_Read TINYINT(1) DEFAULT 0 AFTER Timestamp;

-- Add index for better query performance on Is_Read
CREATE INDEX idx_is_read ON Message(Is_Read);

-- Optional: Update existing messages to mark them as read
-- Uncomment the line below if you want to mark all existing messages as read
-- UPDATE Message SET Is_Read = 1 WHERE Timestamp < NOW();

-- Verify the change
DESCRIBE Message;
