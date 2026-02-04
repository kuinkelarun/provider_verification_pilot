# Provider Verification Dashboard - Quick Start Guide

## Overview
This Flask-based dashboard is designed to **display and analyze pre-processed provider verification data**. It does NOT perform verification - it visualizes data that has already been processed by your backend verification tool.

## Architecture Change Summary
- **OLD**: Upload raw data → Backend processing → Display results
- **NEW**: Upload pre-processed verification results → Store → Display with multi-file filtering

## What You Need

### Pre-Processed CSV/Excel Files
Your files must contain verification results with these columns:

**Required Columns:**
- `Provider Name` - Healthcare provider's full name
- `NPI` - National Provider Identifier (10 digits)

**Recommended Columns:**
- `Address` - Verified street address
- `City` - City name
- `State` - State abbreviation
- `ZIP Code` - 5-digit ZIP code
- `Specialty` - Medical specialty
- `Phone` - Contact phone number
- `Email` - Email address
- `Confidence Score` - Verification confidence (0-100% or 0.0-1.0)
- `Status` - Verification status: `verified`, `needs_review`, or `failed`
- `Sources` - Data sources consulted (comma-separated list)
- `Discrepancies` - Any issues or notes (comma-separated)

### Sample File Format
```csv
Provider Name,NPI,Address,City,State,ZIP Code,Specialty,Phone,Email,Confidence Score,Status,Sources,Discrepancies
"Dr. Sarah Johnson",1234567890,"123 Medical Plaza Dr","Boston","MA","02115","Cardiology","617-555-0100","sjohnson@example.org","95%","verified","NPPES,CMS,State Board",""
"Dr. Michael Chen",1234567891,"456 Healthcare Blvd","Cambridge","MA","02138","Internal Medicine","617-555-0101","mchen@example.com","72%","needs_review","NPPES","Phone not confirmed"
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

The app will start at: `http://localhost:5000`

### 3. Upload Your Data
1. Go to `http://localhost:5000`
2. Drag and drop your pre-processed CSV/Excel file
3. Click "Process File"
4. View results on the dashboard

## Features

### Multi-File Support
- Upload multiple verification result files
- Track upload history
- Filter dashboard by specific file or view all files combined

### Advanced Filtering
- **Search**: Filter by provider name or NPI
- **File**: View specific file or all files
- **Status**: Filter by verified/needs_review/failed
- **Confidence**: Filter by high (>80%), medium (50-80%), or low (<50%)
- **City**: Filter by city
- **ZIP Code**: Search by ZIP code

### Data Persistence
- All uploaded files are stored in `./data_storage/`
- Upload history tracked in `upload_history.json`
- Each file's data stored separately as `{file_id}.json`

### Export
- Export filtered data to CSV
- Export all data or specific file data
- Exports include all verification details

## File Structure
```
├── app.py                          # Main Flask application
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
├── data_storage/                  # Persistent data storage (auto-created)
│   ├── upload_history.json        # Upload tracking
│   └── {file_id}.json            # Individual file data
└── uploads/                       # Temporary file storage (auto-created)
```

## Important Notes

### This Dashboard Does NOT:
- ❌ Perform provider verification
- ❌ Call external APIs for data validation
- ❌ Process raw provider data
- ❌ Connect to Databricks or backend services

### This Dashboard DOES:
- ✅ Display pre-processed verification results
- ✅ Support multiple file uploads with history tracking
- ✅ Provide advanced filtering and search
- ✅ Calculate summary statistics
- ✅ Export filtered data to CSV
- ✅ Store data persistently

## Data Flow

```
Your Backend Tool
      ↓
Verification Results (CSV/Excel)
      ↓
Upload to Dashboard
      ↓
Parse & Store (JSON)
      ↓
Display with Filters
      ↓
Export (if needed)
```

## Column Name Flexibility

The CSV parser handles variations in column names:
- `Provider Name` = `provider_name` = `Provider_Name` = `ProviderName`
- `Confidence Score` can be: percentage (85%) or decimal (0.85)
- `Sources` can be: comma-separated string
- Missing optional columns are handled gracefully

## Troubleshooting

### "No data found" Error
- Make sure you've uploaded at least one file
- Check that `data_storage/upload_history.json` exists
- Verify CSV has required columns: Provider Name, NPI

### Confidence Scores Not Displaying
- Ensure column is named `Confidence Score` or `confidence_score`
- Values should be 0-100 (or 0.0-1.0)
- Can include % symbol: "85%" or just number: 85

### Status Not Showing Correctly
- Status column should contain: `verified`, `needs_review`, or `failed`
- Case-insensitive: "Verified" = "VERIFIED" = "verified"

### File History Not Loading
- Files stored in `data_storage/` directory
- Each upload creates two entries:
  1. `upload_history.json` - metadata
  2. `{file_id}.json` - actual data
- Don't manually edit these files

## Next Steps

1. **Test with Sample Data**: Use the provided `sample_verification_results.csv`
2. **Upload Your Data**: Upload your actual verification results
3. **Explore Filters**: Test different filter combinations
4. **Export Results**: Export filtered data for reporting

## Support & Customization

To customize:
- **Styling**: Edit `static/css/style.css`
- **Column Mapping**: Modify `utils/data_formatter.py` - `parse_uploaded_data()`
- **Filters**: Update `templates/dashboard.html` and `static/js/dashboard.js`
- **Storage**: Configured in `app.py` - `DATA_STORAGE` path

## Performance Notes

- Dashboard tested with 1000+ providers per file
- Pagination set to 50 rows per page
- All filtering happens client-side (fast)
- File filter triggers server reload (loads specific file data)

---

**Version**: 2.0 (Updated for pre-processed data display)  
**Last Updated**: 2024
