# Architecture Change Summary

## Overview of Changes

This document summarizes the major architectural changes made to the Provider Verification Dashboard based on the updated requirement that **CSV/Excel files already contain pre-processed verification data**.

## Key Requirement Change

**BEFORE:**
> "Upload raw provider data → Send to backend for verification → Display results"

**AFTER:**
> "Upload pre-processed verification results → Store → Display with multi-file filtering"

**User's Clarification:**
> "The data we will be uploading will already be processed by the backend tool, and the CSV or Excel will have all the metrics and values such as provider name, address, phone, email, confidence score, and many more."

---

## Architectural Changes

### 1. Removed Backend Integration
**Files Affected:**
- `app.py` - Removed all backend_connector imports and calls
- `utils/backend_connector.py` - No longer needed (can be deleted)

**Changes:**
- Removed `MOCK_DATA_MODE` flag
- Removed `BACKEND_URL` configuration
- Removed `/process` endpoint for backend communication
- Upload now directly parses CSV instead of sending to backend

### 2. Added Persistent Storage
**New Storage Structure:**
```
data_storage/
  ├── upload_history.json        # Tracks all uploaded files
  └── {file_id}.json            # Individual file data
      ├── metadata (filename, upload_time, row_count)
      └── data (array of verification results)
```

**Files Affected:**
- `app.py` - Added `DATA_STORAGE` path configuration
- `app.py` - Modified `/upload` route to save to JSON
- `app.py` - Modified `/dashboard` route to load from JSON

**Benefits:**
- Multi-file support with history tracking
- Data persists across sessions
- Can view historical uploads
- Can filter by specific file

### 3. Direct CSV Parsing
**Files Affected:**
- `utils/data_formatter.py` - Complete rewrite

**Old Function:**
- `generate_mock_results()` - Generated fake verification data

**New Function:**
- `parse_uploaded_data()` - Parses pre-processed CSV with flexible column mapping

**Features:**
- Handles column name variations (case-insensitive, underscore/space variations)
- Normalizes confidence scores (handles percentages and decimals)
- Normalizes status values (verified/needs_review/failed)
- Parses comma-separated sources and discrepancies
- Validates required fields (provider_name, npi)
- Handles missing optional fields gracefully

### 4. Multi-File Dashboard
**Files Affected:**
- `templates/dashboard.html` - Added file filter dropdown
- `static/js/dashboard.js` - Added file filtering logic
- `app.py` - Dashboard route now supports `?file_id=xxx` query parameter

**New Features:**
- View all files combined or filter by specific file
- Upload history sidebar showing all uploaded files
- File metadata display (filename, upload time, row count)

### 5. Enhanced Filtering
**Files Affected:**
- `templates/dashboard.html` - Added city and zipcode filters
- `static/js/dashboard.js` - Added city and zipcode filtering logic
- `static/css/style.css` - Added `.filter-input` styles

**New Filters:**
- File selection (dropdown)
- City (dropdown with unique values)
- ZIP Code (text input with search)

**Existing Filters:**
- Search (provider name, NPI)
- Status (verified/needs_review/failed)
- Confidence (high/medium/low)

### 6. Updated Export Functionality
**Files Affected:**
- `app.py` - Modified `/export` route
- `templates/dashboard.html` - Updated export button logic

**Changes:**
- Export now supports `?file_id=xxx` query parameter
- Can export specific file or all files
- Filename includes file_id: `provider_data_export_{file_id}_{timestamp}.csv`

---

## Code Changes by File

### app.py
**Removed:**
- `from utils.backend_connector import send_to_backend, check_backend_health`
- `MOCK_DATA_MODE` configuration flag
- `generate_mock_results()` calls
- `/process` route for backend integration

**Added:**
- `DATA_STORAGE = './data_storage'` path
- `upload_history.json` tracking
- File ID generation using UUID
- JSON storage for each uploaded file
- Query parameter support for file filtering

**Modified Routes:**
1. **`/upload`** (POST)
   - Now parses CSV directly using `parse_uploaded_data()`
   - Saves to `{file_id}.json`
   - Updates `upload_history.json`
   - Returns success with file metadata

2. **`/dashboard`** (GET)
   - Accepts `?file_id=xxx` query parameter
   - Loads from JSON storage instead of session
   - Loads all files or specific file based on parameter
   - Adds `file_id` to each result for filtering
   - Extracts unique cities for filter dropdown
   - Passes uploaded_files list for file dropdown

3. **`/export`** (GET)
   - Accepts `?file_id=xxx` query parameter
   - Exports specific file or all files
   - Includes file_id in exported filename

4. **`/health`** (GET)
   - Changed from showing mock mode to showing file count

**New Route:**
- **`/api/files`** (GET) - Returns upload history as JSON

### utils/data_formatter.py
**Completely Rewritten:**

**Removed Functions:**
- `generate_mock_results()` - No longer needed

**New Functions:**
1. **`parse_uploaded_data(df, file_id)`**
   - Parses pre-processed verification data from DataFrame
   - Flexible column name mapping with variations
   - Handles different data formats:
     - Confidence: percentage (85%) or decimal (0.85)
     - Status: various formats → normalized to verified/needs_review/failed
     - Sources: comma-separated string → list
     - Discrepancies: comma-separated string → list
   - Validates required fields
   - Returns list of parsed results

**Updated Functions:**
1. **`format_results_for_display(results)`**
   - Simplified to work with pre-parsed data
   - Ensures all fields have default values
   - No longer computes status (already in data)

2. **`calculate_summary_stats(results)`**
   - Unchanged - still calculates summary metrics

**Column Mapping Logic:**
```python
Column Name Variations Supported:
- "Provider Name" = "provider_name" = "Provider_Name" = "ProviderName"
- "Confidence Score" = "confidence_score" = "Confidence" = "Score"
- Handles: underscores, spaces, mixed case
```

### templates/dashboard.html
**Added:**
1. File filter dropdown
   ```html
   <select id="fileFilter" class="filter-select">
     <option value="all">All Files</option>
     {% for file in uploaded_files %}
     <option value="{{ file.id }}">{{ file.filename }}</option>
     {% endfor %}
   </select>
   ```

2. City filter dropdown
   ```html
   <select id="cityFilter" class="filter-select">
     <option value="all">All Cities</option>
     {% for city in cities %}
     <option value="{{ city }}">{{ city }}</option>
     {% endfor %}
   </select>
   ```

3. ZIP code filter input
   ```html
   <input type="text" id="zipcodeFilter" class="filter-input" 
          placeholder="ZIP Code">
   ```

**Modified:**
1. Table rows - Added data attributes:
   ```html
   data-file-id="{{ result.file_id }}"
   data-city="{{ result.city }}"
   data-zipcode="{{ result.zip_code }}"
   ```

2. Export function - Now uses query parameter:
   ```javascript
   window.location.href = '/export?file_id=' + fileFilter;
   ```

3. Reset filters - Added new filters:
   ```javascript
   document.getElementById('fileFilter').value = 'all';
   document.getElementById('cityFilter').value = 'all';
   document.getElementById('zipcodeFilter').value = '';
   ```

### static/js/dashboard.js
**Added:**
1. File filter event listener:
   ```javascript
   if (fileFilter) {
     fileFilter.addEventListener('change', handleFileFilterChange);
   }
   ```

2. File filter change handler:
   ```javascript
   function handleFileFilterChange() {
     const fileId = document.getElementById('fileFilter').value;
     if (fileId === 'all') {
       window.location.href = '/dashboard';
     } else {
       window.location.href = '/dashboard?file_id=' + fileId;
     }
   }
   ```

3. City and zipcode filter event listeners
4. City and zipcode filtering logic in `applyFilters()`

**Modified:**
- `applyFilters()` function now includes city and zipcode filtering
- Added filter logic:
  ```javascript
  const rowCity = row.dataset.city || '';
  const matchesCity = cityFilter === 'all' || rowCity === cityFilter;
  
  const rowZipcode = row.dataset.zipcode || '';
  const matchesZipcode = zipcodeFilter === '' || 
                        rowZipcode.toLowerCase().includes(zipcodeFilter);
  ```

### static/css/style.css
**Added:**
- `.filter-input` class for ZIP code search input
- Styling matches existing `.filter-select` and `.search-input`

### templates/upload.html
**Modified:**
1. Updated subtitle:
   - OLD: "Upload your provider data file to begin verification"
   - NEW: "Upload pre-processed provider verification data"

2. Updated drop zone text:
   - OLD: "Drag and drop your file here"
   - NEW: "Drag and drop your verification results file here"

3. Updated instructions:
   - Added new columns: Email, Confidence Score, Status, Sources, Discrepancies
   - Added note explaining data should be pre-processed
   - Updated download link to sample file

### New Files Created
1. **`sample_data/sample_verification_results.csv`**
   - 20 sample providers with complete verification data
   - Includes all expected columns
   - Shows various statuses and confidence scores

2. **`static/sample_verification_results.csv`**
   - Copy of sample file for download link

3. **`QUICKSTART_V2.md`**
   - Updated quick start guide
   - Explains new architecture
   - Includes sample file format
   - Troubleshooting guide

4. **`ARCHITECTURE_CHANGES.md`** (this file)
   - Complete documentation of changes

---

## Data Model Changes

### Old Data Flow
```
Upload CSV
    ↓
Store in session
    ↓
Send to backend API
    ↓
Wait for backend processing
    ↓
Receive results
    ↓
Display in dashboard
    ↓
Clear session on new upload
```

### New Data Flow
```
Upload Pre-Processed CSV
    ↓
Parse CSV with flexible column mapping
    ↓
Generate unique file_id (UUID)
    ↓
Save to data_storage/{file_id}.json
    ↓
Update upload_history.json
    ↓
Load from JSON storage
    ↓
Display with multi-file filtering
    ↓
Data persists (not cleared)
```

### Storage Schema

**upload_history.json:**
```json
[
  {
    "file_id": "abc123...",
    "filename": "providers_jan2024.csv",
    "upload_time": "2024-01-15T10:30:00",
    "row_count": 150
  },
  {
    "file_id": "def456...",
    "filename": "providers_feb2024.csv",
    "upload_time": "2024-02-01T14:20:00",
    "row_count": 200
  }
]
```

**{file_id}.json:**
```json
{
  "metadata": {
    "file_id": "abc123...",
    "filename": "providers_jan2024.csv",
    "upload_time": "2024-01-15T10:30:00",
    "row_count": 150
  },
  "data": [
    {
      "provider_name": "Dr. Sarah Johnson",
      "npi": "1234567890",
      "address": "123 Medical Plaza Dr",
      "city": "Boston",
      "state": "MA",
      "zip_code": "02115",
      "specialty": "Cardiology",
      "phone": "617-555-0100",
      "email": "sjohnson@example.org",
      "confidence_score": 95,
      "status": "verified",
      "sources": ["NPPES", "CMS", "State Board"],
      "discrepancies": [],
      "file_id": "abc123..."
    }
  ]
}
```

---

## Feature Comparison

| Feature | Old Version | New Version |
|---------|------------|-------------|
| Backend Integration | ✅ Required | ❌ Removed |
| Mock Data Mode | ✅ Yes | ❌ No longer needed |
| Data Persistence | ❌ Session only | ✅ JSON storage |
| Multi-File Support | ❌ No | ✅ Yes |
| File History | ❌ No | ✅ Yes |
| File Filter | ❌ No | ✅ Yes |
| City Filter | ❌ No | ✅ Yes |
| ZIP Code Filter | ❌ No | ✅ Yes |
| Flexible CSV Parsing | ❌ No | ✅ Yes |
| Column Variations | ❌ Exact match | ✅ Flexible |
| Data Processing | ❌ Backend | ✅ Frontend parsing |

---

## Testing Checklist

### Basic Functionality
- [ ] Upload sample CSV file
- [ ] Verify file appears in upload history
- [ ] Check data displays correctly in dashboard
- [ ] Verify summary statistics are correct

### Filtering
- [ ] Search by provider name
- [ ] Search by NPI
- [ ] Filter by status (all three)
- [ ] Filter by confidence level
- [ ] Filter by city
- [ ] Filter by ZIP code
- [ ] Reset all filters

### Multi-File
- [ ] Upload second CSV file
- [ ] Verify both files in upload history
- [ ] Switch between files using file filter
- [ ] View "All Files" - verify combined data
- [ ] Check row counts match

### Export
- [ ] Export all data
- [ ] Export specific file
- [ ] Verify exported CSV format
- [ ] Check filename includes file_id

### Edge Cases
- [ ] Upload CSV with missing optional columns
- [ ] Upload CSV with column name variations
- [ ] Upload CSV with percentage confidence scores
- [ ] Upload CSV with decimal confidence scores
- [ ] Upload CSV with various status formats
- [ ] Upload file with no data
- [ ] Try to view dashboard with no uploads

---

## Migration Notes

### For Users Migrating from Old Version

1. **Data Migration:**
   - Old session-based data will be lost
   - Re-upload your verification results files
   - Old mock data is no longer available

2. **Backend Service:**
   - No longer required for this dashboard
   - Backend verification tool runs separately
   - This dashboard only displays results

3. **File Format:**
   - Update your export scripts to include all verification columns
   - Ensure CSV includes: confidence_score, status, sources
   - See sample file for exact format

### Breaking Changes

1. **`/upload` endpoint:**
   - No longer accepts `backend_url` parameter
   - No longer returns `batch_id`
   - Returns `file_id` instead

2. **`/dashboard` route:**
   - No longer uses `/dashboard/<batch_id>` path parameter
   - Now uses `/dashboard?file_id=xxx` query parameter
   - `file_id=all` or no parameter shows all files

3. **`/export` route:**
   - No longer uses `/export/<batch_id>` path parameter
   - Now uses `/export?file_id=xxx` query parameter

4. **Session storage:**
   - No longer stores data in Flask session
   - Uses JSON file storage
   - Data persists across server restarts

---

## Configuration Changes

### app.py Configuration

**Removed:**
```python
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000/api/verify')
MOCK_DATA_MODE = os.environ.get('MOCK_DATA_MODE', 'True').lower() == 'true'
```

**Added:**
```python
DATA_STORAGE = os.path.join(os.getcwd(), 'data_storage')
```

### Environment Variables

**No Longer Needed:**
- `BACKEND_URL`
- `MOCK_DATA_MODE`

**Still Used:**
- `FLASK_ENV` - development/production
- `SECRET_KEY` - for session management (minimal use now)

---

## Performance Considerations

### Old Version
- Waited for backend API response (slow)
- Session storage limited by memory
- Single file at a time
- No data persistence

### New Version
- Instant CSV parsing (fast)
- JSON file storage (scalable)
- Multiple files supported
- Data persists (no re-upload needed)

### Recommendations
- For very large files (>10MB), consider pagination in CSV parsing
- For 100+ files, consider adding file archiving
- For high-traffic deployments, consider database instead of JSON files

---

## Future Enhancements

Potential improvements for future versions:

1. **Database Integration:**
   - Replace JSON storage with SQLite/PostgreSQL
   - Enable complex queries and aggregations

2. **Advanced Analytics:**
   - Trend analysis across multiple uploads
   - Comparison between files
   - Historical confidence score tracking

3. **File Management:**
   - Delete uploaded files
   - Rename files
   - Archive old files
   - File size limits and quotas

4. **Batch Operations:**
   - Bulk export multiple files
   - Merge files
   - Split files by criteria

5. **Visualization:**
   - Charts for confidence distribution
   - Geographic heatmaps
   - Specialty breakdowns
   - Status pie charts

---

## Support & Maintenance

### Common Issues

**Issue: "No data found" error**
- Solution: Upload at least one file first
- Check: `data_storage/upload_history.json` exists

**Issue: Filters not working**
- Solution: Check browser console for JavaScript errors
- Ensure: All data attributes present in table rows

**Issue: CSV parsing errors**
- Solution: Verify required columns (Provider Name, NPI)
- Check: Column names match expected variations

### Debug Mode

To enable debug logging:
```python
# In app.py
app.config['DEBUG'] = True
```

### Logs Location

- Application logs: Console output
- Error logs: Flask default error handling
- Upload logs: Check `upload_history.json` timestamps

---

## Version History

**Version 1.0** (Original)
- Backend-integrated verification
- Mock data mode
- Session-based storage
- Single file support

**Version 2.0** (Current)
- Pre-processed data display
- No backend dependency
- Persistent JSON storage
- Multi-file support with history
- Enhanced filtering (city, ZIP)
- Flexible CSV parsing

---

**Document Version**: 2.0  
**Last Updated**: 2024  
**Author**: Development Team
