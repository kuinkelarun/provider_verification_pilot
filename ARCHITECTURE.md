# System Architecture

## Overview

Healthcare Provider Verification Dashboard is a Flask web application that queries provider data from Databricks and displays it in an interactive dashboard. It uses a dynamic table discovery mechanism to find provider data across the Databricks schema.

---

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│          (upload_list.html / dashboard.html)               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FLASK WEB SERVER (app.py)                  │
│                                                             │
│  Routes:                                                    │
│  • GET  /                 - Load csv_upload_details table  │
│  • GET  /dashboard        - Search & load provider data    │
│  • GET  /export           - Generate CSV export            │
│  • GET  /health           - Health check endpoint          │
└────────────┬───────────────────────────┬────────────────────┘
             │                           │
             ▼                           ▼
    ┌──────────────────┐      ┌─────────────────────┐
    │  UTILS MODULE    │      │  STATIC ASSETS      │
    │                  │      │                     │
    │ • databricks_    │      │ • style.css         │
    │   connector.py   │      │ • dashboard.js      │
    │ • data_formatter │      │ • base.html         │
    │   .py            │      │ • error.html        │
    └─────────┬────────┘      └─────────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │   DATABRICKS SQL WAREHOUSE  │
    │                             │
    │ • csv_upload_details (meta) │
    │ • batch_process_output (v1) │
    │ • Other provider tables      │
    │ • Dynamic table discovery   │
    └─────────────────────────────┘
```

---

## Data Flow Diagram

### 1. Landing Page (Batch Selection)
```
User opens http://localhost:8080/
    │
    ├─> Flask app.index()
    │   └─> databricks.load_table_data('csv_upload_details')
    │       └─> Returns: [{csv_file_id: '0001', csv_file_name: 'Batch 1', ...}, ...]
    │
    └─> Render upload_list.html with batch list
        └─> User clicks "View Providers"
            └─> Navigate to /dashboard?csv_file_id=0001
```

### 2. Dashboard Page (Dynamic Table Discovery & Data Display)
```
Browser navigates to /dashboard?csv_file_id=0001
    │
    ├─> Flask app.dashboard()
    │
    ├─> SEARCH PHASE:
    │   ├─> databricks.list_available_tables()
    │   │   └─> Returns: [table1, table2, table3, ...]
    │   │
    │   └─> For each table:
    │       └─> Query: SELECT * WHERE csv_file_id = '0001' LIMIT 1
    │           └─> First table with results is the target
    │
    ├─> LOAD PHASE:
    │   └─> databricks.load_table_data(target_table, csv_file_id='0001')
    │       └─> Returns: [{provider_1}, {provider_2}, ...]
    │       └─> Raw JSON with nested fields
    │
    ├─> FORMAT PHASE:
    │   └─> For each provider record:
    │       ├─> data_formatter.parse_json_data() 
    │       │   └─> Deserialize JSON strings (address_json, contacts_json, etc)
    │       │
    │       └─> data_formatter.format_results_for_display()
    │           └─> Transform to display format:
    │               • Extract operating_hours from operational_status_value_*
    │               • Map all fields to dashboard schema
    │               • Return 50+ formatted fields
    │
    └─> RENDER PHASE:
        └─> Pass formatted results to dashboard.html
            └─> Jinja2 renders table with provider data
            └─> JavaScript applies formatting:
                • Phone number formatting
                • Provider name Title Case
                • Modal click handlers
            └─> Display with export button
```

### 3. CSV Export
```
User clicks "Export CSV"
    │
    ├─> Browser calls /export?csv_file_id=0001
    │
    ├─> Flask app.export()
    │   ├─> Uses same table discovery as dashboard
    │   ├─> Loads data
    │   ├─> Formats results
    │   └─> Generates temporary CSV file
    │
    └─> Returns CSV file for download
```

---

## Database Schema

### Table: csv_upload_details
Metadata about uploaded batches:
```
csv_file_id       (String)    - Unique batch identifier
csv_file_name     (String)    - Display name
upload_time       (Timestamp) - When uploaded
uploaded_by       (String)    - User who uploaded
```

### Table: batch_process_output (and other provider tables)
Provider verification data (one table per csv_file_id or shared):
```
csv_file_id       (String)    - Links to csv_upload_details
provider_name     (String)    
npi               (String)    
phone             (String)    
email             (String)    
address           (String)    
city              (String)    
state             (String)    
zip               (String)    
specialty         (String)    
confidence_score  (Float)     
status            (String)    - "Verified" | "Needs Review" | "Failed"
rank              (Integer)   
fax               (String)    
operational_status_value_1 to _5 (String) - Operating hours JSON
address_json      (String)    - Nested address data
contacts_json     (String)    - Nested contact data
[Additional 40+ fields]
```

---

## Key Components

### app.py (Flask Application)
Main entry point with 4 routes:

**`index()` - GET /**
- Loads csv_upload_details table
- Renders upload_list.html with batch list
- User selects which batch to view

**`dashboard()` - GET /dashboard?csv_file_id=X**
- Receives csv_file_id parameter
- Searches all tables for matching csv_file_id
- Loads first matching table's data
- Formats results and renders dashboard.html
- **Key Logic**: Dynamic table discovery

**`export()` - GET /export?csv_file_id=X**
- Uses same table discovery logic
- Generates CSV from formatted results
- Returns file for download

**`health()` - GET /health**
- Checks Databricks connection
- Returns status for monitoring

---

### utils/databricks_connector.py
Manages Databricks SQL connection:

**`__init__(host, token, http_path, catalogs, schemas)`**
- Initializes SQL connection with credentials

**`load_table_data(table_name, filters=None, limit=None)`**
- Queries table with optional WHERE clause
- Returns list of dict records

**`list_available_tables()`**
- Lists all tables in configured schema
- Used for dynamic table discovery

**`query(sql)`**
- Executes arbitrary SQL queries
- Returns raw results

---

### utils/data_formatter.py
Transforms Databricks data for display:

**`parse_json_data(json_str)`**
- Deserializes JSON string fields
- Handles nested structures like address_json, contacts_json

**`format_results_for_display(results)`**
- Maps Databricks fields to dashboard fields
- Extracts operating_hours from operational_status_value_1..5
- Returns array of formatted provider records

**`extract_operating_hours()`**
- Parses time ranges from operational_status fields
- Formats as "Day: time range" on separate lines

---

### templates/

**base.html** - Layout template with header and navigation

**upload_list.html** - Batch selection page
- Displays all batches from csv_upload_details
- Click "View Providers" to go to dashboard
- Shows loading spinner during page transition

**dashboard.html** - Main results page
- Summary metrics (total, verified, needs review, failed)
- Filterable provider table
- Click row to view details modal
- Export CSV button
- Loading spinner during initial load

**error.html** - Error display page

---

### static/

**css/style.css**
- Complete responsive styling
- Color variables for healthcare theme
- Mobile-first design
- Animations for loading spinner

**js/dashboard.js**
- Phone number formatting
- Provider name Title Case conversion
- Modal interactions
- Table filtering and search

---

## Data Transformation Pipeline

```
Raw Databricks Record:
{
  "provider_name": "dr john smith",
  "phone": "5551234567",
  "address_json": "{\"street\": \"123 Main St\", \"suite\": \"Ste 100\"}",
  "operational_status_value_1": "Monday: 7:00am – 6:00pm, Tuesday: 7:00am – 6:00pm"
}

                    ↓ parse_json_data()

Parsed Record:
{
  "provider_name": "dr john smith",
  "phone": "5551234567",
  "address_json_parsed": {"street": "123 Main St", "suite": "Ste 100"},
  "operational_status_value_1": "Monday: 7:00am – 6:00pm, Tuesday: 7:00am – 6:00pm"
}

                    ↓ format_results_for_display()

Display Record:
{
  "provider_name": "Dr John Smith",
  "phone": "555-123-4567",
  "address": "123 Main St, Ste 100",
  "operating_hours": "Monday: 7:00am – 6:00pm\nTuesday: 7:00am – 6:00pm\n...",
  [... 45 more formatted fields ...]
}

                    ↓ Jinja2 Template + JavaScript

HTML Rendered:
<tr>
  <td><a href="tel:555-123-4567">555-123-4567</a></td>
  <td>Dr John Smith</td>
  ...
</tr>
```

---

## Dynamic Table Discovery Algorithm

**Problem**: A csv_file_id can exist in ANY table in the Databricks schema, not just one predetermined table.

**Solution**: Query all tables sequentially until finding the target csv_file_id.

```
ALGORITHM FindTableWithCSVFileID(csv_file_id):
  tables = list_available_tables()  // All tables in schema
  
  FOR each table IN tables:
    IF table == "csv_upload_details":
      SKIP  // Metadata table, not data table
    
    query = "SELECT * FROM table WHERE csv_file_id = ? LIMIT 1"
    result = execute(query, csv_file_id)
    
    IF result NOT EMPTY:
      RETURN table  // Found it!
  
  RETURN None  // csv_file_id not found in any table
```

**Performance**: First query typically returns match in 1-2 seconds for schemas with 10+ tables.

---

## Loading Flow

1. **Upload List Page** → **Dashboard Page Navigation**
   - Click "View Providers" button
   - Loading spinner shows immediately
   - sessionStorage flag set: `isLoadingProviders = true`
   - Browser navigates to /dashboard?csv_file_id=X

2. **Dashboard Page Load**
   - Flask processes request (0.5-2s)
   - Dynamically discovers table with csv_file_id
   - Loads and formats data
   - HTML page renders with data pre-loaded
   - JavaScript detects sessionStorage flag
   - Spinner continues 90-100% completion
   - Spinner hides when page fully interactive

3. **User Sees**
   - 0-100% progress spinner
   - Then instant display of fully loaded dashboard

---

## Error Handling

| Error | Handled By | Response |
|-------|-----------|----------|
| Missing csv_file_id parameter | app.dashboard() | 400 error page |
| csv_file_id not found in any table | app.dashboard() | 404 error page |
| Databricks connection fails | DatabricksConnector | 500 error with message |
| Invalid .env config | app initialization | Error on startup |

---

## Configuration

All settings via `.env` file:

```env
ENABLE_DATABRICKS=true
DATABRICKS_HOST=your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_HTTP_PATH=/sql/1.0/endpoints/...
DATABRICKS_CATALOGS=databricks_poc
DATABRICKS_SCHEMAS=default
DATABRICKS_TABLE_PATTERN=*
DATABRICKS_CACHE_DURATION=5
FLASK_ENV=production
FLASK_SECRET_KEY=...
```

---

## Deployment

**Development**: `python app.py` → http://localhost:8080

**Production**: Databricks Apps or cloud container service with .env configured

---

## Summary

The application follows a clean layered architecture:
1. **Presentation Layer**: HTML/CSS/JS templates
2. **Application Layer**: Flask routes in app.py
3. **Data Layer**: Databricks SQL queries
4. **Transformation Layer**: Data formatter utilities

Key insight: **Dynamic table discovery** allows the dashboard to work with any csv_file_id without pre-configured mappings, making it flexible for different batch sources.
