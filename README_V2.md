# Provider Verification Dashboard v2.0

A Flask-based web dashboard for **displaying and analyzing pre-processed provider verification data**. This application visualizes verification results that have already been processed by your backend verification tool.

## 🎯 Purpose

This dashboard **DOES NOT** perform provider verification. It is designed to:
- ✅ Display pre-processed verification results from CSV/Excel files
- ✅ Support multiple file uploads with persistent storage
- ✅ Provide advanced filtering and search capabilities
- ✅ Calculate summary statistics and metrics
- ✅ Export filtered data to CSV

## 📋 Requirements

Your CSV/Excel files must contain **pre-processed verification data** with these columns:

### Required
- **Provider Name** - Healthcare provider's full name
- **NPI** - National Provider Identifier (10 digits)

### Recommended
- **Address** - Verified street address
- **City** - City name
- **State** - State abbreviation (MA, NY, etc.)
- **ZIP Code** - 5-digit ZIP code
- **Specialty** - Medical specialty
- **Phone** - Contact phone number
- **Email** - Email address
- **Confidence Score** - Verification confidence (0-100% or 0.0-1.0)
- **Status** - `verified`, `needs_review`, or `failed`
- **Sources** - Data sources consulted (comma-separated)
- **Discrepancies** - Issues found (comma-separated)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Dashboard
Open your browser to: **http://localhost:5000**

### 4. Upload Your Data
1. Drag and drop your pre-processed CSV/Excel file
2. Click "Process File"
3. View results on the dashboard

## 📁 Project Structure

```
.
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── utils/
│   ├── data_formatter.py          # CSV parsing and data formatting
│   └── file_handler.py            # File upload validation
├── templates/
│   ├── base.html                  # Base template
│   ├── upload.html                # Upload page
│   ├── dashboard.html             # Results dashboard
│   └── error.html                 # Error page
├── static/
│   ├── css/style.css              # Styling
│   ├── js/dashboard.js            # Dashboard interactivity
│   └── sample_verification_results.csv  # Sample file
├── data_storage/                  # Persistent data (auto-created)
│   ├── upload_history.json        # Upload tracking
│   └── {file_id}.json            # Individual file data
├── uploads/                       # Temporary storage (auto-created)
└── sample_data/
    └── sample_verification_results.csv  # Sample data
```

## ✨ Features

### Multi-File Support
- Upload multiple verification result files
- Track complete upload history
- Filter dashboard by specific file or view all combined
- Each file stored separately with unique ID

### Advanced Filtering
- **Search**: Filter by provider name or NPI (real-time)
- **File**: View specific file or all files
- **Status**: Filter by verified/needs_review/failed
- **Confidence**: Filter by high (>80%), medium (50-80%), low (<50%)
- **City**: Filter by city (dropdown of unique values)
- **ZIP Code**: Search by ZIP code (text input)

### Data Visualization
- Summary metrics cards (total, verified, review, failed)
- Color-coded status badges
- Confidence score bars with visual indicators
- Source count display with tooltips
- Address change highlighting

### Export Functionality
- Export all data or specific file data
- Maintains all verification details
- Includes timestamps in filename
- CSV format for easy analysis

### Data Persistence
- All uploads stored in `./data_storage/` directory
- Upload history tracked with metadata
- Data persists across server restarts
- Can revisit historical uploads

## 🎨 User Interface

### Upload Page
- Drag-and-drop file upload
- File format validation
- Sample file download
- Clear instructions for expected format

### Dashboard
- Clean, healthcare-focused design
- Responsive layout
- Real-time filtering
- Sortable table columns
- Pagination (50 rows per page)
- Export button with dynamic filename

## 🔧 Configuration

### app.py Settings
```python
UPLOAD_FOLDER = './uploads'          # Temporary file storage
DATA_STORAGE = './data_storage'       # Persistent data storage
MAX_FILE_SIZE = 50 * 1024 * 1024     # 50 MB limit
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
```

### Environment Variables
```bash
FLASK_ENV=development    # development or production
SECRET_KEY=your-secret-key-here
```

## 📊 Sample Data

A sample file with 20 providers is included:
- **Location**: `static/sample_verification_results.csv`
- **Download**: Available from upload page
- **Format**: Complete verification data with all columns

## 🔍 Column Name Flexibility

The CSV parser handles variations in column names:

```python
"Provider Name" = "provider_name" = "Provider_Name" = "ProviderName"
"Confidence Score" = "confidence_score" = "Confidence" = "Score"
"ZIP Code" = "zip_code" = "Zipcode" = "Zip"
```

- Case-insensitive matching
- Handles underscores and spaces
- Accepts multiple naming conventions

## 💡 Usage Examples

### Example 1: Upload Single File
1. Upload `providers_jan2024.csv` with 150 providers
2. Dashboard displays all 150 providers
3. Use filters to narrow down results
4. Export filtered data to CSV

### Example 2: Multi-File Analysis
1. Upload `providers_jan2024.csv` (150 providers)
2. Upload `providers_feb2024.csv` (200 providers)
3. Use file filter to switch between files
4. Select "All Files" to view combined 350 providers
5. Compare metrics between uploads

### Example 3: Filtering Workflow
1. Select specific file from dropdown
2. Filter by city: "Boston"
3. Filter by status: "needs_review"
4. Search for specific provider name
5. Export filtered results for review

## 🐛 Troubleshooting

### "No data found" Error
- **Cause**: No files uploaded yet
- **Solution**: Upload at least one CSV/Excel file
- **Check**: Verify `data_storage/upload_history.json` exists

### Confidence Scores Not Displaying
- **Cause**: Column name mismatch or invalid format
- **Solution**: Use "Confidence Score" or "confidence_score" column
- **Format**: Values 0-100 or 0.0-1.0, with or without % symbol

### Status Not Showing Correctly
- **Cause**: Invalid status values
- **Solution**: Use `verified`, `needs_review`, or `failed`
- **Note**: Case-insensitive matching supported

### File Filter Empty
- **Cause**: No upload history found
- **Solution**: Upload files appear in history after processing
- **Check**: Verify files in `data_storage/` directory

### CSV Parsing Errors
- **Cause**: Missing required columns
- **Solution**: Ensure "Provider Name" and "NPI" columns exist
- **Check**: Compare to sample CSV format

## 📚 Documentation

- **[QUICKSTART_V2.md](QUICKSTART_V2.md)** - Detailed setup guide
- **[ARCHITECTURE_CHANGES.md](ARCHITECTURE_CHANGES.md)** - Architecture documentation
- **Sample CSV** - Download from upload page

## 🔐 Security Notes

- File uploads validated for type and size
- Secure filename handling (werkzeug)
- No external API calls
- All data stored locally
- No sensitive data transmission

## 🚦 API Endpoints

### Public Routes
- **`GET /`** - Upload page
- **`POST /upload`** - Process file upload
- **`GET /dashboard`** - Display results (optional `?file_id=xxx`)
- **`GET /export`** - Export data (optional `?file_id=xxx`)
- **`GET /health`** - Health check endpoint

### API Routes
- **`GET /api/files`** - Get upload history (JSON)

## 🎯 Performance

- **Tested**: 1000+ providers per file
- **Pagination**: 50 rows per page
- **Filtering**: Client-side (instant)
- **File switching**: Server-side (loads specific file)
- **Storage**: JSON files (fast for moderate scale)

## 📈 Future Enhancements

Potential improvements:
- Database integration (SQLite/PostgreSQL)
- Advanced analytics and charts
- File management (delete, rename, archive)
- Batch operations (merge, split files)
- User authentication
- API for programmatic access

## 🤝 Contributing

This is an internal tool. For suggestions or issues, contact the development team.

## 📄 License

Internal use only - Accenture AFS-GenWizard Deployment

## 📞 Support

For questions or issues:
1. Check **QUICKSTART_V2.md** for setup help
2. Review **ARCHITECTURE_CHANGES.md** for technical details
3. Contact the development team

---

**Version**: 2.0 (Pre-Processed Data Display)  
**Last Updated**: 2024  
**Architecture**: Flask + Pandas + JavaScript  
**Purpose**: Visualization of pre-processed provider verification data
