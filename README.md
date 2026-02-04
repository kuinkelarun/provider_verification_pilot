# Flask Provider Verification Dashboard

A modern, intuitive web dashboard for healthcare provider data verification, designed to run on Databricks.

## 🎯 Features

- **File Upload**: Drag-and-drop CSV/Excel file upload with preview
- **Real-time Verification**: Integration with Databricks backend for AI-powered verification
- **Interactive Dashboard**: Filter, search, and sort through thousands of provider records
- **Confidence Scoring**: Visual indicators for verification confidence levels
- **Export Functionality**: Download results as CSV
- **Modern UI**: Clean, professional design optimized for healthcare operations

## 📁 Project Structure

```
flask-provider-dashboard/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment configuration template
├── README.md                       # This file
│
├── templates/
│   ├── base.html                   # Base template
│   ├── upload.html                 # File upload screen
│   ├── dashboard.html              # Results dashboard
│   └── error.html                  # Error page
│
├── static/
│   ├── css/
│   │   └── style.css              # Complete styling
│   └── js/
│       └── dashboard.js           # Dashboard interactivity
│
└── utils/
    ├── __init__.py
    ├── file_handler.py            # File upload handling
    ├── backend_connector.py       # Databricks backend integration
    └── data_formatter.py          # Data formatting utilities
```

## 🚀 Quick Start

### Phase 1: Local Development with Mock Data

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Dashboard**
   - Open browser to: `http://localhost:8080`
   - Upload a CSV/Excel file with provider data
   - View mock verification results

### Phase 2: Backend Integration

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Databricks credentials
   ```

2. **Update app.py**
   ```python
   # In app.py, change:
   MOCK_DATA_MODE = False
   ```

3. **Implement Backend Connection**
   - Edit `utils/backend_connector.py`
   - Choose your integration method:
     - Databricks Jobs API
     - REST API endpoint
     - Delta table query
   - See comments in file for examples

## 📋 Required File Format

Your CSV/Excel file should include these columns:

- **Provider Name** (required) - Full name of healthcare provider
- **NPI** (required) - National Provider Identifier
- **Address** - Street address
- **City** - City name
- **State** - State abbreviation
- **ZIP Code** - 5-digit ZIP code
- **Specialty** - Medical specialty
- **Phone** - Contact phone number

### Sample Data

Download the template from the upload page or create a file like this:

```csv
Provider Name,NPI,Address,City,State,ZIP Code,Specialty,Phone
Dr. John Smith,1234567890,123 Main St,Boston,MA,02101,Cardiology,617-555-0100
Dr. Jane Doe,9876543210,456 Oak Ave,Cambridge,MA,02139,Pediatrics,617-555-0200
```

## 🎨 UI Components

### Upload Screen
- Drag-and-drop file upload
- File validation and preview
- Clear instructions and template download

### Dashboard
- **Summary Cards**: Total, Verified, Needs Review, Failed counts
- **Filters**: Search by name/NPI, filter by status and confidence
- **Results Table**: Sortable columns, pagination, visual indicators
- **Export**: Download filtered results as CSV

### Status Indicators
- ✓ **Verified** (Green) - High confidence (>80%)
- ⚠ **Needs Review** (Yellow) - Medium confidence (50-80%)
- ✗ **Failed** (Red) - Low confidence (<50%)

## 🔧 Configuration Options

### Application Settings (app.py)

```python
# Mock data mode for development
MOCK_DATA_MODE = True  # Set to False for production

# File upload limits
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Upload folder
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
```

### Backend Integration (utils/backend_connector.py)

Three integration options are provided:

1. **Databricks Jobs API** - Trigger notebook/job runs
2. **REST API** - Custom backend endpoint
3. **Delta Tables** - Direct table access via PySpark

See inline comments for implementation examples.

## 🏗️ Deployment to Databricks

### Option 1: Databricks Apps (Recommended)

1. **Package Application**
   ```bash
   zip -r provider-dashboard.zip * -x "*.pyc" "__pycache__/*"
   ```

2. **Upload to Databricks Workspace**
   - Navigate to Workspace
   - Upload zip file
   - Extract in desired location

3. **Configure Databricks App**
   - Create new Databricks App
   - Point to app.py
   - Set environment variables
   - Configure compute resources

4. **Access Your App**
   - Use generated Databricks App URL
   - Share with data stewardship team

### Option 2: Databricks Notebooks

1. Convert Flask routes to notebook cells
2. Use `%sh` magic commands for Flask startup
3. Use Databricks SQL for data access

## 🔐 Security Considerations

- **Authentication**: Currently open access (POC mode)
  - For production: Add Flask-Login or OAuth integration
- **File Validation**: Already implemented (file type, size limits)
- **SQL Injection**: Use parameterized queries for Delta table access
- **Environment Variables**: Never commit `.env` file
- **HTTPS**: Ensure Databricks Apps use HTTPS endpoints

## 📊 Performance Tips

1. **Large Files**: For >10,000 rows, consider:
   - Batch processing with progress indicators
   - Background job submission
   - Async result polling

2. **Pagination**: Default 50 rows per page
   - Adjust `rowsPerPage` in dashboard.js

3. **Filtering**: Client-side for <1000 rows
   - Server-side for larger datasets

## 🐛 Troubleshooting

### File Upload Issues
- Check file size (<50MB)
- Verify file format (CSV, XLSX, XLS)
- Ensure required columns present

### Backend Connection Issues
- Verify Databricks credentials in `.env`
- Check network access to Databricks workspace
- Review `backend_connector.py` implementation

### Display Issues
- Clear browser cache
- Check browser console for JavaScript errors
- Verify all static files loaded correctly

## 🔄 Development Workflow

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run with mock data
python app.py

# Access at http://localhost:8080
```

### Backend Integration Testing
```bash
# Set environment variables
export DATABRICKS_HOST="https://..."
export DATABRICKS_TOKEN="..."

# Disable mock mode in app.py
# Test with real backend
python app.py
```

## 📝 Next Steps

### Immediate (Phase 1)
- [x] Complete UI design
- [x] Mock data generation
- [x] File upload/validation
- [x] Dashboard display
- [x] Filtering/search/sort

### Backend Integration (Phase 2)
- [ ] Connect to Databricks backend
- [ ] Test with real verification results
- [ ] Handle async processing
- [ ] Add progress indicators

### Production Readiness (Phase 3)
- [ ] Add user authentication
- [ ] Implement error logging
- [ ] Add monitoring/alerts
- [ ] Performance optimization
- [ ] Security audit

## 👥 Team Integration Questions

Before backend integration, clarify:

1. **Backend Interface**: How do we trigger batch processing?
   - Python function call?
   - REST API endpoint?
   - Databricks Jobs API?

2. **Data Format**: What's the structure of results?
   - Delta table schema?
   - JSON response format?
   - Required fields?

3. **Authentication**: How do we authenticate?
   - Service principal?
   - Personal access token?
   - OAuth?

4. **Deployment**: Where should this run?
   - Databricks Apps?
   - Separate web server?
   - Notebook environment?

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📄 License

Internal use - Healthcare Provider Directory Project

---

**Built with ❤️ for Data Stewardship Teams**
#   p r o v i d e r _ v e r i f i c a t i o n _ p i l o t  
 