-- ============================================================================
-- Healthcare Provider Directory - Databricks Setup Script
-- ============================================================================
-- This script helps set up the required Databricks resources for the app
-- Run these commands in a Databricks SQL Warehouse or Notebook
-- ============================================================================

-- Step 1: Create Catalog (if not exists)
-- ============================================================================
CREATE CATALOG IF NOT EXISTS databricks_poc
COMMENT 'Catalog for Healthcare Provider Directory application';

-- Use the catalog
USE CATALOG databricks_poc;

-- Step 2: Create Schema (if not exists)
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS default
COMMENT 'Default schema for provider verification data';

-- Use the schema
USE SCHEMA default;

-- Step 3: Verify or Create csv_upload_details Table
-- ============================================================================
-- This table stores metadata about uploaded CSV files

CREATE TABLE IF NOT EXISTS csv_upload_details (
  csv_file_id STRING NOT NULL COMMENT 'Unique identifier for the uploaded CSV file',
  filename STRING COMMENT 'Original filename of the uploaded CSV',
  upload_time TIMESTAMP COMMENT 'Timestamp when the file was uploaded',
  total_rows INT COMMENT 'Total number of rows in the CSV',
  processed_rows INT COMMENT 'Number of rows successfully processed',
  status STRING COMMENT 'Processing status: pending, processing, completed, failed',
  uploaded_by STRING COMMENT 'User who uploaded the file',
  source_system STRING COMMENT 'System or source of the data',
  file_size_mb DOUBLE COMMENT 'File size in megabytes',
  processing_duration_seconds INT COMMENT 'Time taken to process in seconds',
  notes STRING COMMENT 'Additional notes or comments'
)
USING DELTA
COMMENT 'Metadata for uploaded provider CSV files'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Step 4: Sample Data for csv_upload_details (for testing)
-- ============================================================================
-- Insert sample records if table is empty

INSERT INTO csv_upload_details 
VALUES 
  (
    'test-001-20260204', 
    'sample_providers.csv', 
    current_timestamp(), 
    100, 
    100, 
    'completed', 
    'admin@accenture.com', 
    'manual_upload', 
    0.5, 
    45, 
    'Test data for application testing'
  );

-- Step 5: Verify batch processing output tables exist
-- ============================================================================
-- List all tables that might contain batch processing results

SHOW TABLES LIKE '*batch_process_output*';

-- Step 6: Example structure for batch processing output tables
-- ============================================================================
-- Your batch processing tables should have at least these columns:

-- CREATE TABLE IF NOT EXISTS batch_process_output_XXXXXX (
--   csv_file_id STRING NOT NULL,
--   source_npi STRING,
--   provider_name STRING,
--   source_provider_name STRING,
--   address STRING,
--   source_address STRING,
--   city STRING,
--   source_city STRING,
--   state STRING,
--   source_state STRING,
--   zipcode STRING,
--   phone STRING,
--   fax STRING,
--   email STRING,
--   facility_name STRING,
--   confidence_measure STRING,  -- High, Medium, Low
--   status STRING,  -- SUCCESS, FAILED
--   addr_source STRING,
--   addr_source_1 STRING,
--   addr_source_2 STRING,
--   addr_source_3 STRING,
--   addr_source_4 STRING,
--   addr_source_5 STRING,
--   phone_source_1 STRING,
--   phone_source_2 STRING,
--   phone_source_3 STRING,
--   phone_source_4 STRING,
--   phone_source_5 STRING,
--   operational_status STRING,
--   operational_status_value_1 STRING,
--   operational_status_value_2 STRING,
--   operational_status_value_3 STRING,
--   operational_status_value_4 STRING,
--   operational_status_value_5 STRING,
--   rank STRING,
--   error_message STRING,
--   llm_parse_error STRING,
--   processed_timestamp TIMESTAMP
-- )
-- USING DELTA;

-- Step 7: Grant Permissions (adjust user/group as needed)
-- ============================================================================
-- Grant SELECT permissions to app users

-- For specific user
-- GRANT SELECT ON TABLE csv_upload_details TO `user@accenture.com`;
-- GRANT SELECT ON SCHEMA default TO `user@accenture.com`;

-- For a group
-- GRANT SELECT ON SCHEMA default TO `data_analysts`;
-- GRANT SELECT ON TABLE csv_upload_details TO `data_analysts`;

-- Step 8: Verify Setup
-- ============================================================================

-- Check catalog exists
SHOW CATALOGS LIKE 'databricks_poc';

-- Check schema exists
SHOW SCHEMAS IN databricks_poc LIKE 'default';

-- Check csv_upload_details table
DESCRIBE TABLE EXTENDED csv_upload_details;

-- Check data in csv_upload_details
SELECT * FROM csv_upload_details LIMIT 10;

-- Count records
SELECT COUNT(*) as total_uploads FROM csv_upload_details;

-- List all tables in schema
SHOW TABLES IN databricks_poc.default;

-- Step 9: Search for tables with csv_file_id column
-- ============================================================================
-- This query finds all tables that have the csv_file_id column
-- (tables that the app can discover dynamically)

SELECT 
  table_catalog,
  table_schema,
  table_name,
  column_name,
  data_type
FROM system.information_schema.columns
WHERE column_name = 'csv_file_id'
  AND table_catalog = 'databricks_poc'
  AND table_schema = 'default'
ORDER BY table_name;

-- Step 10: Test Query (simulate app behavior)
-- ============================================================================
-- This simulates what the app does to find data

-- Get list of csv_file_ids
SELECT DISTINCT csv_file_id FROM csv_upload_details;

-- Test loading data for a specific csv_file_id
-- Replace 'test-001-20260204' with an actual csv_file_id
SET VAR csv_file_id = 'test-001-20260204';

-- Find which table has this csv_file_id
SELECT 
  table_name,
  COUNT(*) as row_count
FROM system.information_schema.tables t
JOIN system.information_schema.columns c 
  ON t.table_catalog = c.table_catalog 
  AND t.table_schema = c.table_schema 
  AND t.table_name = c.table_name
WHERE t.table_catalog = 'databricks_poc'
  AND t.table_schema = 'default'
  AND c.column_name = 'csv_file_id'
  AND t.table_name NOT LIKE '%csv_upload_details%'
GROUP BY table_name;

-- Step 11: Optimization (for better performance)
-- ============================================================================

-- Optimize tables
OPTIMIZE csv_upload_details;

-- Update table statistics
ANALYZE TABLE csv_upload_details COMPUTE STATISTICS;

-- Vacuum old files (only if you want to clean up old versions)
-- VACUUM csv_upload_details RETAIN 168 HOURS;  -- Keep 7 days of history

-- Step 12: Create sample batch output table (for testing)
-- ============================================================================
CREATE TABLE IF NOT EXISTS batch_process_output_test (
  csv_file_id STRING NOT NULL,
  source_npi STRING,
  provider_name STRING,
  address STRING,
  city STRING,
  state STRING,
  zipcode STRING,
  phone STRING,
  confidence_measure STRING,
  status STRING,
  processed_timestamp TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA;

-- Insert sample verification data
INSERT INTO batch_process_output_test VALUES
  ('test-001-20260204', '1234567890', 'Dr. John Smith', '123 Main St', 'Boston', 'MA', '02101', '617-555-0100', 'High', 'SUCCESS', current_timestamp()),
  ('test-001-20260204', '9876543210', 'Dr. Jane Doe', '456 Oak Ave', 'Cambridge', 'MA', '02139', '617-555-0200', 'High', 'SUCCESS', current_timestamp()),
  ('test-001-20260204', '5555555555', 'Dr. Bob Wilson', '789 Elm St', 'Somerville', 'MA', '02144', '617-555-0300', 'Medium', 'SUCCESS', current_timestamp());

-- Verify test data
SELECT * FROM batch_process_output_test;

-- ============================================================================
-- Setup Complete!
-- ============================================================================
-- Next steps:
-- 1. Note your SQL Warehouse HTTP path
-- 2. Generate a Personal Access Token
-- 3. Configure environment variables in Databricks Apps
-- 4. Deploy the application
-- ============================================================================

-- Useful commands for monitoring:

-- Check table sizes
SELECT 
  table_name,
  num_files,
  size_in_bytes / 1024 / 1024 as size_mb
FROM (
  DESCRIBE DETAIL csv_upload_details
);

-- Monitor recent uploads
SELECT 
  csv_file_id,
  filename,
  upload_time,
  status,
  total_rows,
  processing_duration_seconds
FROM csv_upload_details
ORDER BY upload_time DESC
LIMIT 20;
