# Healthcare Provider Directory - Databricks Apps Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment](#post-deployment)

---

## Prerequisites

### Required Databricks Resources

✅ **SQL Warehouse**
- Type: Serverless or Provisioned
- Size: Small (for testing) or Medium (for production)
- Status: Running
- Note: Copy the HTTP Path from the "Connection Details" tab

✅ **Unity Catalog Access**
- Catalog: `databricks_poc` (or your catalog name)
- Schema: `default` (or your schema name)
- Permissions: READ access

✅ **Required Tables**
Your workspace must have these tables:
- `databricks_poc.default.csv_upload_details`
  - Columns: `csv_file_id`, `upload_time`, `filename`, etc.
- Batch processing output tables with `csv_file_id` column

✅ **Databricks Apps Access**
- Databricks Runtime: 13.0 or higher
- Workspace: Premium or Enterprise tier
- Permissions: Can create and manage apps

✅ **Personal Access Token (PAT)**
- Scope: Workspace access
- Lifetime: Set appropriate expiration
- Permissions: SQL execution, table read access

---

## Pre-Deployment Checklist

### 1. Verify SQL Warehouse

```sql
-- Test your SQL Warehouse connection
SELECT current_catalog(), current_schema();
```

### 2. Verify Tables Exist

```sql
-- Check csv_upload_details table
SELECT * FROM databricks_poc.default.csv_upload_details LIMIT 5;

-- List all tables in schema
SHOW TABLES IN databricks_poc.default;
```

### 3. Verify Table Schema

```sql
-- Check csv_upload_details structure
DESCRIBE TABLE databricks_poc.default.csv_upload_details;

-- Ensure batch output tables have csv_file_id column
DESCRIBE TABLE databricks_poc.default.batch_process_output_XXXXXX;
```

### 4. Create Personal Access Token

1. Go to **Databricks Workspace → Settings → Developer → Access Tokens**
2. Click **Generate New Token**
3. Name: `Healthcare-Provider-App`
4. Lifetime: `90 days` (or as per policy)
5. **Copy and save the token securely** (you won't see it again)

### 5. Get SQL Warehouse HTTP Path

1. Go to **SQL Warehouses** in Databricks
2. Select your warehouse
3. Go to **Connection Details** tab
4. Copy the **HTTP Path** (format: `/sql/1.0/warehouses/xxxxx`)

---

## Deployment Steps

### Step 1: Prepare Application Files

Ensure your project has these files:
```
Healthcare-Provider-Directory/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── app.yaml                  # Databricks Apps config
├── .env.example             # Environment template
├── utils/
│   ├── __init__.py
│   ├── databricks_connector.py
│   ├── data_formatter.py
│   ├── file_handler.py
│   └── backend_connector.py
├── templates/
│   ├── base.html
│   ├── upload_list.html
│   ├── dashboard.html
│   └── error.html
└── static/
    ├── css/style.css
    └── js/dashboard.js
```

### Step 2: Create .env File for Configuration

Create a `.env` file (for reference, not deployed):
```bash
# Databricks Connection
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...your-token...
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx

# Catalog Configuration
DATABRICKS_CATALOGS=databricks_poc
DATABRICKS_SCHEMAS=default
DATABRICKS_TABLE_PATTERN=batch_process_output,csv_upload_details
DATABRICKS_CACHE_DURATION=5

# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-here-change-in-production
ENABLE_DATABRICKS=true
```

### Step 3: Deploy to Databricks Apps

#### Option A: Using Databricks UI (Recommended)

1. **Navigate to Databricks Apps**
   - Go to your Databricks workspace
   - Click on **Apps** in the left sidebar
   - Click **Create App**

2. **Upload Application Code**
   - **Name**: `healthcare-provider-directory`
   - **Source**: Upload files or connect Git repository
   - Upload all files from your project directory

3. **Configure Environment Variables**
   
   In the Databricks Apps UI, set these environment variables:
   
   ```
   FLASK_APP=app.py
   FLASK_ENV=production
   ENABLE_DATABRICKS=true
   
   DATABRICKS_HOST=<your-workspace>.cloud.databricks.com
   DATABRICKS_TOKEN=<your-PAT>  # Use secrets for production
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/<warehouse-id>
   
   DATABRICKS_CATALOGS=databricks_poc
   DATABRICKS_SCHEMAS=default
   DATABRICKS_TABLE_PATTERN=batch_process_output,csv_upload_details
   DATABRICKS_CACHE_DURATION=5
   
   FLASK_SECRET_KEY=<generate-secure-random-key>
   ```

4. **Configure Compute Resources**
   - **Memory**: 2 GB (recommended)
   - **CPU**: 1 core
   - **Python Version**: 3.9 or higher

5. **Set Start Command**
   ```bash
   flask run --host=0.0.0.0 --port=8080
   ```

6. **Deploy**
   - Click **Deploy** or **Start App**
   - Wait for deployment to complete (usually 2-5 minutes)

#### Option B: Using Databricks CLI

```bash
# Install Databricks CLI (if not already installed)
pip install databricks-cli

# Configure CLI
databricks configure --token

# Create app configuration
databricks apps create healthcare-provider-directory \
  --source-directory . \
  --python-version 3.9

# Deploy app
databricks apps deploy healthcare-provider-directory
```

#### Option C: Using Git Integration

1. **Push code to Git repository**
   ```bash
   git add .
   git commit -m "Prepare for Databricks deployment"
   git push origin main
   ```

2. **In Databricks Apps**
   - Select **Git** as source
   - Enter repository URL
   - Select branch: `main`
   - Set path to application: `/`

3. **Configure and Deploy**

---

## Configuration

### Using Databricks Secrets (Recommended for Production)

Instead of plain text environment variables, use Databricks Secrets:

1. **Create Secret Scope**
   ```bash
   databricks secrets create-scope --scope healthcare-provider-app
   ```

2. **Add Secrets**
   ```bash
   databricks secrets put --scope healthcare-provider-app \
     --key databricks-token
   
   databricks secrets put --scope healthcare-provider-app \
     --key flask-secret-key
   ```

3. **Update app.yaml to use secrets**
   ```yaml
   env:
     - name: DATABRICKS_TOKEN
       valueFrom:
         secretKeyRef:
           name: healthcare-provider-app
           key: databricks-token
     - name: FLASK_SECRET_KEY
       valueFrom:
         secretKeyRef:
           name: healthcare-provider-app
           key: flask-secret-key
   ```

### Generate Secure Flask Secret Key

```python
# Run this in Python to generate a secure key
import secrets
print(secrets.token_hex(32))
```

---

## Verification

### Step 1: Check App Status

1. Go to **Databricks Apps** in the UI
2. Find `healthcare-provider-directory`
3. Status should show: **Running** ✅

### Step 2: Access the Application

1. Click on the app name
2. Copy the **App URL** (format: `https://xxx.cloud.databricks.com/apps/healthcare-provider-directory`)
3. Open in browser

### Step 3: Test Health Endpoint

```bash
curl https://your-workspace.cloud.databricks.com/apps/healthcare-provider-directory/health
```

Expected response:
```json
{
  "status": "healthy",
  "databricks": "connected",
  "timestamp": "2026-02-04T10:30:00"
}
```

### Step 4: Test Upload List Page

Navigate to: `https://your-app-url/`

Expected: You should see a list of uploaded files from `csv_upload_details` table

### Step 5: Test Dashboard

1. Click on a `csv_file_id` from the list
2. Should redirect to: `/dashboard?csv_file_id=xxx`
3. Verify provider data is displayed
4. Check filters work (city, status)
5. Test export functionality

---

## Troubleshooting

### Issue 1: "Databricks connection not configured"

**Cause**: Environment variables not set correctly

**Solution**:
```bash
# Verify environment variables in Databricks Apps UI
# Ensure DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH are set
# Check ENABLE_DATABRICKS=true
```

### Issue 2: "Failed to load csv_upload_details"

**Cause**: Table doesn't exist or no permissions

**Solution**:
```sql
-- Verify table exists
SHOW TABLES IN databricks_poc.default LIKE 'csv_upload_details';

-- Check permissions
SELECT * FROM databricks_poc.default.csv_upload_details LIMIT 1;

-- Grant permissions if needed
GRANT SELECT ON TABLE databricks_poc.default.csv_upload_details TO `user@example.com`;
```

### Issue 3: "No table found containing data for csv_file_id"

**Cause**: Batch output tables don't have data or missing csv_file_id column

**Solution**:
```sql
-- Find tables with csv_file_id column
SELECT table_catalog, table_schema, table_name, column_name
FROM system.information_schema.columns
WHERE column_name = 'csv_file_id'
  AND table_catalog = 'databricks_poc'
  AND table_schema = 'default';

-- Check data exists
SELECT DISTINCT csv_file_id 
FROM databricks_poc.default.batch_process_output_XXXXX;
```

### Issue 4: "databricks-sql-connector not installed"

**Cause**: Missing dependency

**Solution**:
```bash
# Add to requirements.txt
databricks-sql-connector>=3.0.0

# Redeploy app
```

### Issue 5: App crashes on startup

**Cause**: SQL Warehouse not running or HTTP path incorrect

**Solution**:
1. Go to **SQL Warehouses** in Databricks
2. Ensure warehouse is **Running** (start if stopped)
3. Verify HTTP path is correct (format: `/sql/1.0/warehouses/xxxxx`)
4. Test connection:
   ```python
   from databricks import sql
   connection = sql.connect(
       server_hostname="your-workspace.cloud.databricks.com",
       http_path="/sql/1.0/warehouses/xxxxx",
       access_token="dapi..."
   )
   ```

### Issue 6: "Connection failed: 401 Unauthorized"

**Cause**: Invalid or expired Personal Access Token

**Solution**:
1. Generate new PAT in Databricks
2. Update `DATABRICKS_TOKEN` environment variable
3. Restart app

### View App Logs

```bash
# Using Databricks CLI
databricks apps logs healthcare-provider-directory

# Or in Databricks UI
# Apps → healthcare-provider-directory → Logs tab
```

---

## Post-Deployment

### 1. Monitor Application

**Check metrics regularly**:
- Response times
- Error rates
- SQL Warehouse usage
- Memory/CPU usage

**Set up alerts** (if available):
- App downtime
- High error rates
- SQL Warehouse throttling

### 2. Performance Optimization

**Enable caching**:
- Table list cache is already enabled (5 min default)
- Increase `DATABRICKS_CACHE_DURATION` if tables don't change often

**SQL Warehouse sizing**:
- Small: Testing, < 10 concurrent users
- Medium: Production, 10-50 concurrent users
- Large: High traffic, > 50 concurrent users

**Consider serverless SQL Warehouse**:
- Automatic scaling
- Pay per query
- No cold start after first query

### 3. Security Best Practices

✅ **Use Databricks Secrets** for sensitive data
✅ **Rotate PAT tokens** regularly (every 90 days)
✅ **Set appropriate expiration** for tokens
✅ **Use Unity Catalog governance** features
✅ **Enable audit logging** for compliance
✅ **Implement row-level security** if needed
✅ **Use HTTPS only** (default in Databricks Apps)

### 4. Backup and Recovery

**App Configuration**:
- Keep `app.yaml` in version control
- Document all environment variables
- Store secrets securely (password manager, Databricks Secrets)

**Database**:
- Delta Lake provides time travel
- Tables are automatically backed up
- Test restore procedures

### 5. Update and Maintenance

**Update application**:
```bash
# Update code in Git repository
git pull origin main

# Redeploy in Databricks Apps UI or CLI
databricks apps deploy healthcare-provider-directory
```

**Update dependencies**:
```bash
# Update requirements.txt
pip list --outdated

# Test locally first
pip install -r requirements.txt

# Deploy updated requirements
```

### 6. Scaling Considerations

**Horizontal scaling**:
- Databricks Apps can auto-scale
- Configure in app settings

**Database optimization**:
- Add indexes if queries are slow
- Partition large tables
- Use Delta Lake optimization commands:
  ```sql
  OPTIMIZE databricks_poc.default.csv_upload_details;
  VACUUM databricks_poc.default.csv_upload_details RETAIN 168 HOURS;
  ```

---

## Quick Reference

### Essential URLs

| Resource | URL Format |
|----------|------------|
| App URL | `https://[workspace].cloud.databricks.com/apps/healthcare-provider-directory` |
| Health Check | `https://[app-url]/health` |
| Upload List | `https://[app-url]/` |
| Dashboard | `https://[app-url]/dashboard?csv_file_id=XXX` |
| Export | `https://[app-url]/export?csv_file_id=XXX` |

### Environment Variables Quick Reference

| Variable | Example | Required |
|----------|---------|----------|
| `DATABRICKS_HOST` | `adb-123.azuredatabricks.net` | ✅ Yes |
| `DATABRICKS_TOKEN` | `dapi...` | ✅ Yes |
| `DATABRICKS_HTTP_PATH` | `/sql/1.0/warehouses/abc123` | ✅ Yes |
| `DATABRICKS_CATALOGS` | `databricks_poc` | ✅ Yes |
| `DATABRICKS_SCHEMAS` | `default` | ✅ Yes |
| `ENABLE_DATABRICKS` | `true` | ✅ Yes |
| `FLASK_SECRET_KEY` | `<random-hex>` | ✅ Yes |
| `DATABRICKS_TABLE_PATTERN` | `batch_process_output` | ⚠️ Optional |
| `DATABRICKS_CACHE_DURATION` | `5` | ⚠️ Optional |

### Support Contacts

- **Databricks Support**: support@databricks.com
- **App Owner**: [Your contact info]
- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) and [CALL_GRAPH.md](CALL_GRAPH.md)

---

## Additional Resources

- [Databricks Apps Documentation](https://docs.databricks.com/en/apps/index.html)
- [Unity Catalog Guide](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- [SQL Warehouse Configuration](https://docs.databricks.com/en/sql/admin/sql-endpoints.html)
- [Flask Deployment Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)

---

## Deployment Checklist

Use this checklist to ensure successful deployment:

- [ ] SQL Warehouse is created and running
- [ ] SQL Warehouse HTTP path copied
- [ ] Unity Catalog and schema exist
- [ ] Required tables exist (`csv_upload_details` + batch output tables)
- [ ] Tables have correct schema (including `csv_file_id` column)
- [ ] Personal Access Token generated
- [ ] All environment variables documented
- [ ] `requirements.txt` is up to date
- [ ] Code pushed to Git repository (if using Git source)
- [ ] Databricks Apps created
- [ ] Environment variables configured in Databricks Apps
- [ ] Secrets configured (for production)
- [ ] App deployed successfully
- [ ] App status shows "Running"
- [ ] Health check endpoint returns 200 OK
- [ ] Upload list page loads
- [ ] Dashboard displays data correctly
- [ ] Export functionality works
- [ ] Logs reviewed for errors
- [ ] Performance monitoring enabled
- [ ] Documentation updated
- [ ] Team notified of deployment

---

**Deployment Date**: _________________

**Deployed By**: _________________

**App URL**: _________________

**Notes**: _________________
