# Healthcare Provider Verification Dashboard

A modern Flask web application for browsing and verifying healthcare provider data stored in Databricks. The dashboard provides an intuitive interface to view provider verification results with filtering, searching, and export capabilities.

---

## 🎯 Features

- **Batch Management**: View all uploaded provider verification batches
- **Dynamic Data Discovery**: Automatically finds provider data across Databricks tables
- **Provider Details**: View comprehensive provider information with operating hours
- **Confidence Scoring**: Visual indicators for verification confidence
- **Export**: Download results as CSV
- **Mobile Responsive**: Works seamlessly on all devices
- **Loading Indicator**: Smooth spinner animation during data loading

---

## 📁 Project Structure

```
Healthcare-Provider-Directory/
├── app.py                          # Main Flask application & route handlers
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
│
├── utils/
│   ├── __init__.py
│   ├── databricks_connector.py     # Databricks connection & table queries
│   ├── data_formatter.py           # JSON parsing & data formatting
│   ├── file_handler.py             # File upload validation (legacy)
│   └── backend_connector.py        # Backend integration (legacy)
│
├── templates/
│   ├── base.html                   # Base HTML template with header
│   ├── upload_list.html            # Landing page - batch selection
│   ├── dashboard.html              # Results dashboard - provider details
│   └── error.html                  # Error display page
│
└── static/
    ├── css/
    │   └── style.css              # Complete responsive styling
    └── js/
        └── dashboard.js           # Client-side interactions
```

---

## 📦 Module Dependencies

**Python Packages** (see `requirements.txt`):

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework for routing & templating |
| Werkzeug | 3.0.1 | WSGI utilities & HTTP handling |
| pandas | 2.1.4 | Data manipulation & CSV processing |
| python-dotenv | 1.0.0 | Load environment variables from `.env` |
| databricks-sql-connector | ≥3.0.0 | Connect to Databricks SQL Warehouse |

---

## 🔧 Python Files Overview

### **app.py** (357 lines)
Main Flask application with route handlers:
- **`index()`** - Loads and displays `csv_upload_details` table (batch listing page)
- **`dashboard()`** - Dynamically finds table containing `csv_file_id`, loads provider data, formats results
- **`export()`** - Generates CSV export of filtered results
- **`health()`** - Health check endpoint for monitoring

**Key Logic**: 
- On dashboard load, searches all tables in Databricks schema for ones containing the requested `csv_file_id`
- Loads matching data and passes to formatter for display

---

### **utils/databricks_connector.py**
Handles all Databricks SQL Warehouse connections:
- **`__init__()`** - Initializes connection with host, token, HTTP path
- **`load_table_data(table_name, filters=None)`** - Query table with optional WHERE clause
- **`list_available_tables()`** - List all accessible tables in schema
- **`query()`** - Execute arbitrary SQL queries

**Usage in app.py**:
```python
databricks.load_table_data('databricks_poc.default.csv_upload_details')
```

---

### **utils/data_formatter.py**
Transforms raw Databricks JSON into display-ready format:
- **`parse_json_data(json_str)`** - Parses nested JSON fields from Databricks records
- **`format_results_for_display(results)`** - Maps Databricks fields to dashboard fields, extracts operating hours
- **`extract_operating_hours()`** - Parses operating hours from `operational_status_value_*` fields

**Data Transformation Pipeline**:
```
Databricks JSON fields → parse_json_data() → format_results_for_display()
→ Dashboard-ready format with:
   - provider_name (Title Case)
   - npi, phone (formatted), email
   - address, city, state, zip
   - specialty, confidence_score
   - operating_hours (one day per line)
```

---

### **utils/file_handler.py**
Validates uploaded files (currently unused - data comes from Databricks):
- `validate_file()` - Check file type & size
- `parse_csv()` - Read CSV file into memory

---

### **utils/backend_connector.py**
Backend integration placeholder (currently unused):
- For future REST API or Databricks Jobs API integration

---

## 🔄 Data Flow

### **1. Landing Page (Batch Selection)**
```
User visits http://localhost:8080/
    ↓
app.index() calls databricks.load_table_data('csv_upload_details')
    ↓
Databricks returns: [{csv_file_id: '0001', csv_file_name: 'Batch 1', ...}, ...]
    ↓
Jinja2 renders upload_list.html with batch list
    ↓
User clicks "View Providers" → navigates to /dashboard?csv_file_id=0001
```

### **2. Dashboard Page (Data Display)**
```
Browser navigates to /dashboard?csv_file_id=0001
    ↓
app.dashboard() receives csv_file_id parameter
    ↓
Search phase:
  - Call databricks.list_available_tables()
  - For each table: query with WHERE csv_file_id = '0001'
  - Return first table with matching records
    ↓
Load phase:
  - databricks.load_table_data(found_table_name) with csv_file_id filter
  - Returns array of provider records (raw JSON from Databricks)
    ↓
Format phase:
  - Call data_formatter.parse_json_data() on each record
  - Parse nested JSON fields: address_json, contacts_json, etc.
  - Call format_results_for_display() to map to display format
    ↓
Render phase:
  - Pass formatted results to dashboard.html template
  - Jinja2 renders table with 50+ provider fields
  - JavaScript applies phone number formatting, name casing
    ↓
Display:
  - Upload list with batch info
  - Summary metrics (total, verified, needs review, etc.)
  - Filterable provider table with modal details on click
  - Export CSV button
```

### **3. Export CSV**
```
User clicks "Export CSV" on dashboard
    ↓
JavaScript calls /export?csv_file_id=0001
    ↓
app.export():
  - Uses same table discovery as dashboard
  - Loads data, formats it
  - Generates temporary CSV file
    ↓
Returns CSV file download to browser
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Databricks workspace with SQL Warehouse
- Access to tables in `databricks_poc.default` schema

### Installation

1. **Clone/download** the project

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (copy template)
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env`** with Databricks credentials:
   ```env
   DATABRICKS_HOST=your-workspace.databricks.com
   DATABRICKS_TOKEN=dapi...
   DATABRICKS_HTTP_PATH=/sql/1.0/endpoints/your-endpoint-id
   DATABRICKS_CATALOGS=databricks_poc
   DATABRICKS_SCHEMAS=default
   ENABLE_DATABRICKS=true
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open browser** to `http://localhost:8080`

---

## 📊 Expected Data Schema

### **csv_upload_details Table**
Stores metadata about uploaded batches:
```
csv_file_id (string)      - Unique identifier for this batch
csv_file_name (string)    - Display name
upload_time (timestamp)   - When batch was uploaded
uploaded_by (string)      - User who uploaded
```

### **Provider Data Tables** (e.g., batch_process_output)
Stores provider records with csv_file_id:
```
csv_file_id (string)      - Links to upload_details
provider_name (string)
npi (string)
phone (string)
email (string)
address (string)
city (string)
state (string)
zip (string)
specialty (string)
confidence_score (float)
status (string)           - Verified, Needs Review, Failed
operational_status_value_1 to _5 (string) - Operating hours JSON
address_json (string)     - Nested address fields
contacts_json (string)    - Nested contact fields
```

---

## 🔍 How Data is Parsed

1. **Raw Databricks Records**: Contain nested JSON in string fields
   ```json
   {
     "provider_name": "Dr. Smith",
     "address_json": "{\"street\": \"123 Main St\", \"building\": \"Suite 100\"}"
   }
   ```

2. **Parse Phase** (`parse_json_data`): Deserializes JSON strings
   ```python
   address_json → parsed dict → extracted fields
   ```

3. **Format Phase** (`format_results_for_display`): Maps to dashboard schema
   ```python
   {
     "provider_name": "Dr. Smith",
     "address": "123 Main St, Suite 100",
     "operating_hours": "Monday: 7:00am – 6:00pm\nTuesday: 7:00am – 6:00pm\n..."
   }
   ```

4. **Display Phase**: Rendered in HTML template with JavaScript formatting
   ```html
   <td>{{ result.provider_name }}</td>  <!-- "Dr. Smith" -->
   <td><a href="tel:{{ result.phone }}">{{ result.phone }}</a></td>  <!-- Clickable phone -->
   ```

---

## 📝 Configuration

Create `.env` file (see `.env.example`):

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_SECRET_KEY=your-secret-key

# Databricks
ENABLE_DATABRICKS=true
DATABRICKS_HOST=your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_HTTP_PATH=/sql/1.0/endpoints/...
DATABRICKS_CATALOGS=databricks_poc
DATABRICKS_SCHEMAS=default
DATABRICKS_TABLE_PATTERN=*
DATABRICKS_CACHE_DURATION=5
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Databricks connection not configured" | Check `.env` file exists and `ENABLE_DATABRICKS=true` |
| "Table not found" | Ensure table exists in `databricks_poc.default` schema |
| "No data for csv_file_id" | Verify csv_file_id exists in some table with matching WHERE clause |
| CSV export fails | Check Databricks token has read access to table |

---

## 📄 License

Proprietary - Accenture AI Pilot

---

## 📞 Support

For issues or questions, check the Databricks connection and ensure tables contain expected data structure.

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
#   p r o v i d e r _ v e r i f i c a t i o n _ p i l o t 
 
 