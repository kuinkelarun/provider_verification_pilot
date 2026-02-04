# 🚀 Deployment Guide - Provider Verification Dashboard

## Overview

This guide covers deploying the Flask Provider Verification Dashboard to Databricks.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Application tested locally with mock data
- [ ] UI/UX approved by stakeholders
- [ ] Backend integration requirements documented
- [ ] Databricks workspace access confirmed
- [ ] Environment variables prepared
- [ ] Sample data for testing available

---

## 🎯 Deployment Options

### Option 1: Databricks Apps (Recommended) ⭐

**Best for**: Production deployment with proper compute resources

#### Step 1: Prepare Application Package

```bash
# In your project directory
cd "c:\Users\arun.kuinkel\OneDrive - Accenture\AFS-GenWizard Deployment\Applications\AI Pilot - Healthcare Provider Directory"

# Create deployment package (exclude unnecessary files)
# Note: Use appropriate commands for your OS
```

#### Step 2: Upload to Databricks Workspace

1. **Navigate to Databricks Workspace**
   - Log into your Databricks workspace
   - Go to Workspace → Users → your_user → Create → Folder
   - Name it: `provider-verification-dashboard`

2. **Upload Files**
   - Upload all project files to this folder
   - Maintain directory structure
   - Upload via UI or CLI

#### Step 3: Configure Databricks App

1. **Create New App**
   ```
   Workspace → Apps → Create App
   ```

2. **Configure Settings**
   ```
   Name: Provider Verification Dashboard
   Source: /Users/your_user/provider-verification-dashboard/app.py
   Command: python app.py
   Environment Variables:
     - FLASK_SECRET_KEY=your-secret-key
     - DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
     - DATABRICKS_TOKEN=your-token
     (Add other env vars from .env.example)
   ```

3. **Select Compute**
   - Cluster type: Single Node
   - Databricks Runtime: 13.3 LTS (Python 3.10)
   - Node type: Standard_DS3_v2 (or equivalent)

4. **Deploy**
   - Click "Deploy"
   - Wait for app to start (2-3 minutes)
   - Note the generated URL

#### Step 4: Test Deployment

1. Access the generated URL
2. Upload sample_providers.csv
3. Verify dashboard displays correctly
4. Test all filters and export

---

### Option 2: Databricks Notebook

**Best for**: Quick prototyping and testing

#### Step 1: Create Notebook

1. **Create new Python notebook** in Databricks
2. **Name it**: `Provider Verification App`

#### Step 2: Install Dependencies

```python
# Cell 1: Install dependencies
%pip install Flask==3.0.0 pandas==2.1.4 openpyxl==3.1.2 xlrd==2.0.1
```

#### Step 3: Copy Application Code

```python
# Cell 2: Import modules
# Copy contents of utils/ files here
# ... (see full implementation in project files)
```

```python
# Cell 3: Flask application
# Copy contents of app.py here
# Modify to run in notebook context
```

#### Step 4: Run Application

```python
# Cell 4: Start Flask server
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8080, app, use_reloader=False, use_debugger=True)
```

---

### Option 3: External Hosting + Databricks Backend

**Best for**: Separation of concerns, scalability

Deploy Flask app separately (Azure App Service, AWS EC2, etc.) and connect to Databricks backend via API.

---

## 🔐 Security Configuration

### Environment Variables

**Never commit these to version control!**

```bash
# Production environment variables
FLASK_SECRET_KEY=generate-secure-key-here  # Use: python -c "import secrets; print(secrets.token_hex(32))"
FLASK_ENV=production

DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef  # Service principal token recommended
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123

BATCH_JOB_ID=your-batch-job-id
```

### Databricks Secrets (Recommended)

Instead of environment variables, use Databricks Secrets:

```python
# In backend_connector.py
from databricks import sql
import dbutils

DATABRICKS_TOKEN = dbutils.secrets.get(scope="provider-verification", key="databricks-token")
```

---

## 🔌 Backend Integration Steps

### 1. Identify Integration Method

**Option A: Databricks Jobs API**
- Trigger existing notebook/job for batch processing
- Poll for results

**Option B: REST API**
- Backend exposes custom API endpoint
- POST file path, GET results

**Option C: Delta Tables**
- Write to input Delta table
- Read from output Delta table

### 2. Implement in `utils/backend_connector.py`

Choose one implementation option from the commented code blocks in the file.

Example (Jobs API):
```python
def process_batch(csv_path, batch_id):
    response = requests.post(
        f"{DATABRICKS_HOST}/api/2.1/jobs/run-now",
        headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
        json={
            "job_id": BATCH_JOB_ID,
            "notebook_params": {
                "csv_path": csv_path,
                "batch_id": batch_id
            }
        }
    )
    return response.json()['run_id']

def get_batch_results(batch_id):
    # Poll job status, then fetch results from Delta table
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    
    results_df = spark.table("provider_verification_results") \
                     .filter(f"batch_id = '{batch_id}'") \
                     .toPandas()
    
    return results_df.to_dict('records')
```

### 3. Update `app.py`

```python
# Change line 19:
MOCK_DATA_MODE = False  # Enable production mode
```

### 4. Test Integration

1. Upload small test file (10-20 providers)
2. Verify backend processing starts
3. Check results appear correctly
4. Validate data format matches expectations

---

## 🧪 Testing Checklist

### Functional Testing

- [ ] File upload (CSV)
- [ ] File upload (Excel XLSX)
- [ ] File upload (Legacy XLS)
- [ ] Large file upload (>1000 rows)
- [ ] File validation errors display correctly
- [ ] Backend integration triggers successfully
- [ ] Results display with correct data
- [ ] All filters work (search, status, confidence)
- [ ] Sorting works on all columns
- [ ] Pagination works correctly
- [ ] Export downloads CSV with correct data
- [ ] Template download works

### UI/UX Testing

- [ ] Upload screen displays properly
- [ ] Dashboard metrics are accurate
- [ ] Table is readable and properly formatted
- [ ] Status badges show correct colors
- [ ] Confidence bars display correctly
- [ ] Responsive design works on mobile
- [ ] No console errors in browser

### Performance Testing

- [ ] Upload 1,000 rows - acceptable speed
- [ ] Upload 10,000 rows - acceptable speed
- [ ] Dashboard loads quickly
- [ ] Filters respond in <1 second
- [ ] Export completes successfully

---

## 📊 Monitoring & Logging

### Application Logs

Add logging to track usage:

```python
# In app.py, add:
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info(f"File upload started: {file.filename}")
    # ... existing code
    logger.info(f"Batch {batch_id} created with {len(df_preview)} rows")
```

### Databricks Monitoring

- Monitor compute usage
- Track API call rates
- Review job execution times
- Set up alerts for failures

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: App won't start in Databricks
- Check Python version compatibility (3.10+)
- Verify all dependencies installed
- Review environment variables

**Issue**: Backend connection fails
- Verify token has correct permissions
- Check network connectivity
- Review Databricks workspace firewall rules

**Issue**: Large files timeout
- Increase Flask timeout settings
- Consider async processing
- Add progress indicators

**Issue**: Memory errors with large datasets
- Optimize pandas operations
- Use chunked processing
- Increase cluster memory

---

## 🔄 Update Procedure

### Rolling Out Updates

1. **Test locally** with mock data
2. **Test in dev environment** with real backend
3. **Deploy to staging** (if available)
4. **Backup current production** version
5. **Deploy to production**
6. **Monitor** for issues
7. **Rollback** if needed

### Version Control

Tag releases:
```bash
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Weekly**: Review logs for errors
- **Monthly**: Check for dependency updates
- **Quarterly**: Performance review and optimization

### Getting Help

- Review error logs in Databricks
- Check browser console for UI issues
- Refer to README.md for documentation
- Contact backend team for integration issues

---

## ✅ Production Readiness Checklist

Before going live:

- [ ] All tests passing
- [ ] Backend integration working
- [ ] Security review completed
- [ ] Environment variables configured
- [ ] Monitoring setup
- [ ] Error handling tested
- [ ] User documentation prepared
- [ ] Stakeholder approval obtained
- [ ] Rollback procedure documented
- [ ] Support plan in place

---

## 🎉 Success!

Your Provider Verification Dashboard is now deployed and ready to help data stewardship teams verify thousands of provider records efficiently!

**Next Steps:**
1. Train users on the interface
2. Gather feedback for improvements
3. Monitor usage and performance
4. Plan Phase 3 enhancements

---

**Deployed with ❤️ for Healthcare Data Quality**
