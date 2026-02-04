# Call Graph - Healthcare Provider Directory Application

## Overview
This document provides a comprehensive call graph showing the function call relationships and dependencies within the Healthcare Provider Directory application.

---

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Flask App (app.py)                      │
│                                                                   │
│  Routes: /, /dashboard, /export, /load-databricks-table,        │
│          /download-template, /health                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ imports & uses
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
        ▼                                               ▼
┌───────────────────┐                         ┌─────────────────────┐
│  DatabricksConnector                        │   data_formatter    │
│  (databricks_connector.py)                  │   (data_formatter.py)│
└───────────────────┘                         └─────────────────────┘
                                                        │
                                                        │
                                              ┌─────────┴─────────┐
                                              │                   │
                                              ▼                   ▼
                                        ┌──────────┐      ┌──────────────┐
                                        │  pandas  │      │   datetime   │
                                        └──────────┘      └──────────────┘
```

---

## Detailed Call Graph by Module

### 1. **app.py** (Main Flask Application)

#### Entry Point: `if __name__ == '__main__'`
```
main()
  └─> app.run()
```

#### Route: `/` (index)
```
index()
  ├─> databricks.load_table_data('databricks_poc.default.csv_upload_details')
  └─> render_template('upload_list.html', uploads=upload_data)
```

#### Route: `/dashboard` (Provider Dashboard)
```
dashboard()
  ├─> request.args.get('csv_file_id')
  ├─> databricks.list_available_tables()
  │   └─> DatabricksConnector.list_available_tables()
  ├─> databricks.load_table_data(table_name, csv_file_id=csv_file_id)
  │   └─> DatabricksConnector.load_table_data()
  ├─> parse_json_data(table_data)
  │   └─> data_formatter.parse_json_data()
  ├─> format_results_for_display(parsed_data)
  │   └─> data_formatter.format_results_for_display()
  └─> render_template('dashboard.html', results=formatted_results, ...)
```

#### Route: `/export` (Export Results)
```
export_results()
  ├─> request.args.get('csv_file_id')
  ├─> databricks.list_available_tables()
  │   └─> DatabricksConnector.list_available_tables()
  ├─> databricks.load_table_data(target_table, csv_file_id=csv_file_id)
  │   └─> DatabricksConnector.load_table_data()
  ├─> parse_json_data(table_data)
  │   └─> data_formatter.parse_json_data()
  ├─> format_results_for_display(parsed_data)
  │   └─> data_formatter.format_results_for_display()
  ├─> pd.DataFrame(formatted_results)
  ├─> df.to_csv(output_path, index=False)
  └─> send_file(output_path, as_attachment=True, ...)
```

#### Route: `/load-databricks-table` (Load Table Data)
```
load_databricks_table()
  ├─> request.get_json()
  ├─> databricks.load_table_data(table_name, limit=100000)
  │   └─> DatabricksConnector.load_table_data()
  ├─> parse_json_data(table_data)
  │   └─> data_formatter.parse_json_data()
  ├─> json.dump({...}, f)
  └─> jsonify({...})
```

#### Route: `/download-template` (Download CSV Template)
```
download_template()
  ├─> pd.DataFrame(template_data)
  ├─> df.to_csv(output_path, index=False)
  └─> send_file(output_path, as_attachment=True, ...)
```

#### Route: `/health` (Health Check)
```
health_check()
  ├─> databricks check
  └─> jsonify({...})
```

---

### 2. **utils/databricks_connector.py** (DatabricksConnector Class)

#### Initialization
```
DatabricksConnector.__init__(host, token, http_path, ...)
  ├─> self.host = host.replace('https://', '')
  ├─> from databricks import sql
  └─> self.sql = sql
```

#### Connection Management
```
_get_connection()
  └─> self.sql.connect(server_hostname, http_path, access_token)
```

#### Cache Validation
```
_is_cache_valid()
  ├─> datetime.now()
  └─> elapsed < timedelta(minutes=self.cache_duration)
```

#### List Available Tables
```
list_available_tables(force_refresh=False)
  ├─> _is_cache_valid()
  ├─> _get_connection()
  ├─> cursor.execute(query)
  ├─> cursor.fetchall()
  ├─> cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
  │   └─> cursor.fetchone()
  ├─> cursor.close()
  ├─> connection.close()
  └─> return tables
```

#### Load Table Data
```
load_table_data(table_name, limit=None, csv_file_id=None)
  ├─> _get_connection()
  ├─> cursor.execute(query)
  ├─> cursor.fetchall()
  ├─> [desc[0] for desc in cursor.description]
  ├─> cursor.close()
  ├─> connection.close()
  └─> return data
```

#### Test Connection
```
test_connection()
  ├─> _get_connection()
  ├─> cursor.execute("SELECT 1")
  ├─> cursor.fetchone()
  ├─> cursor.close()
  └─> connection.close()
```

---

### 3. **utils/data_formatter.py** (Data Formatting Utilities)

#### Parse JSON Data
```
parse_json_data(json_data)
  ├─> isinstance(json_data, dict) check
  ├─> for record in json_data:
  │   ├─> record.get('source_npi', '')
  │   ├─> record.get('provider_name')
  │   ├─> record.get('confidence_measure', 'Medium')
  │   ├─> record.get('status', 'SUCCESS')
  │   ├─> list(dict.fromkeys(sources))  # Remove duplicates
  │   └─> parsed_data.append(result)
  └─> return (parsed_data, validation_errors)
```

#### Parse Uploaded Data
```
parse_uploaded_data(df)
  ├─> df.copy()
  ├─> df_lower.columns = [str(col).strip().lower() for col in df.columns]
  ├─> for idx, row in df_lower.iterrows():
  │   ├─> pd.isna(value) check
  │   ├─> str(value).strip()
  │   ├─> float(conf_str) if conf_str else 0
  │   ├─> status.lower()
  │   ├─> [s.strip() for s in sources_str.split(',')]
  │   ├─> datetime.now().isoformat()
  │   └─> parsed_data.append(record)
  └─> return (parsed_data, validation_errors)
```

#### Format Results for Display
```
format_results_for_display(results)
  ├─> for result in results:
  │   ├─> result.get('provider_name', 'Unknown')
  │   ├─> result.get('npi', 'N/A')
  │   ├─> result.get('confidence_score', 0)
  │   ├─> result.get('status', 'pending')
  │   └─> formatted.append(formatted_result)
  └─> return formatted
```

#### Calculate Summary Statistics
```
calculate_summary_stats(results)
  ├─> len(results)
  ├─> sum(1 for r in results if r.get('status') == 'verified')
  ├─> sum(r.get('confidence_score', 0) for r in results) / total
  ├─> set() for all_sources
  ├─> all_sources.update(r.get('sources', []))
  └─> return summary_dict
```

---

### 4. **utils/file_handler.py** (File Handling Utilities)

#### Validate File
```
validate_file(filename)
  └─> filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

#### Handle File Upload
```
handle_file_upload(file, upload_folder)
  ├─> secure_filename(file.filename)
  ├─> datetime.now().strftime('%Y%m%d_%H%M%S')
  ├─> os.makedirs(upload_folder, exist_ok=True)
  ├─> file.save(filepath)
  └─> return filepath
```

#### Get File Size
```
get_file_size(filepath)
  ├─> os.path.getsize(filepath)
  └─> return f"{size_mb:.2f} MB"
```

---

### 5. **utils/backend_connector.py** (Backend Connector - Stub Implementation)

#### Process Batch
```
process_batch(csv_path, batch_id)
  └─> return batch_id  # Mock mode
  
  # Future implementations (commented out):
  # ├─> requests.post(f"{DATABRICKS_HOST}/api/2.1/jobs/run-now", ...)
  # ├─> spark.createDataFrame(df)
  # └─> spark_df.write.format("delta").saveAsTable(...)
```

#### Get Batch Results
```
get_batch_results(batch_id)
  └─> raise NotImplementedError("Backend integration not yet configured")
  
  # Future implementations (commented out):
  # ├─> requests.get(api_url, ...)
  # ├─> spark.table("provider_verification_results").filter(...)
  # └─> cursor.execute(f"SELECT * FROM provider_verification_results...")
```

#### Check Batch Status
```
check_batch_status(batch_id)
  └─> return {'status': 'completed', ...}  # Mock mode
  
  # Future implementations (commented out):
  # └─> requests.get(f"{DATABRICKS_HOST}/api/2.1/jobs/runs/get", ...)
```

---

## Dependency Graph

### External Libraries

```
Flask Application
├── Flask (web framework)
│   ├── render_template
│   ├── request
│   ├── jsonify
│   └── send_file
│
├── pandas (data manipulation)
│   ├── DataFrame
│   ├── read_csv
│   └── to_csv
│
├── databricks-sql-connector
│   └── databricks.sql
│       └── connect()
│
├── Python Standard Library
│   ├── os (file operations)
│   ├── json (JSON handling)
│   ├── datetime (timestamps)
│   ├── tempfile (temporary files)
│   └── re (regex patterns)
│
├── dotenv
│   └── load_dotenv
│
└── werkzeug
    └── secure_filename
```

---

## Data Flow Diagram

```
┌──────────────┐
│   User       │
└──────┬───────┘
       │ HTTP Request
       ▼
┌──────────────────────────────────────────┐
│  Flask Routes (app.py)                   │
│  ├─ / (Upload List)                      │
│  ├─ /dashboard (Provider Dashboard)      │
│  ├─ /export (Export CSV)                 │
│  └─ /health (Health Check)               │
└──────┬───────────────────────────────────┘
       │
       │ calls
       │
       ├────────────────────┬───────────────────────┐
       │                    │                       │
       ▼                    ▼                       ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Databricks   │  │  Data Formatter  │  │  File Handler    │
│ Connector    │  │  (utils)         │  │  (utils)         │
└──────┬───────┘  └──────┬───────────┘  └──────────────────┘
       │                 │
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│ Databricks   │  │  Parsed/         │
│ Tables       │  │  Formatted Data  │
│              │  │                  │
└──────────────┘  └──────────────────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  HTML Templates │
       │  (Jinja2)       │
       └────────┬────────┘
                │
                ▼ HTTP Response
       ┌─────────────────┐
       │   User Browser  │
       └─────────────────┘
```

---

## Function Call Hierarchy

### High-Level Call Hierarchy

```
app.py (Main Application)
│
├─> Initialization
│   ├─> load_dotenv()
│   ├─> Flask(__name__)
│   └─> DatabricksConnector(host, token, http_path, ...)
│
├─> Route: /
│   ├─> databricks.load_table_data()
│   │   ├─> _get_connection()
│   │   ├─> cursor.execute()
│   │   └─> cursor.fetchall()
│   └─> render_template()
│
├─> Route: /dashboard
│   ├─> databricks.list_available_tables()
│   │   ├─> _is_cache_valid()
│   │   ├─> _get_connection()
│   │   └─> cursor.execute()
│   ├─> databricks.load_table_data()
│   ├─> parse_json_data()
│   │   └─> [processes each record]
│   ├─> format_results_for_display()
│   │   └─> [formats each result]
│   └─> render_template()
│
├─> Route: /export
│   ├─> databricks.list_available_tables()
│   ├─> databricks.load_table_data()
│   ├─> parse_json_data()
│   ├─> format_results_for_display()
│   ├─> pd.DataFrame()
│   ├─> df.to_csv()
│   └─> send_file()
│
├─> Route: /load-databricks-table
│   ├─> databricks.load_table_data()
│   ├─> parse_json_data()
│   └─> jsonify()
│
├─> Route: /download-template
│   ├─> pd.DataFrame()
│   ├─> df.to_csv()
│   └─> send_file()
│
└─> Route: /health
    └─> jsonify()
```

---

## Module Interaction Matrix

| Module | Depends On | Used By |
|--------|-----------|---------|
| **app.py** | databricks_connector, data_formatter, Flask, pandas, dotenv | - (entry point) |
| **databricks_connector.py** | databricks.sql, datetime, re | app.py |
| **data_formatter.py** | pandas, datetime, json | app.py |
| **file_handler.py** | os, werkzeug, datetime | (currently unused - prepared for future upload feature) |
| **backend_connector.py** | requests, os, datetime | (currently unused - stub for future backend integration) |

---

## Critical Path Analysis

### Most Frequently Called Functions

1. **databricks.load_table_data()** - Called by:
   - `index()` route
   - `dashboard()` route
   - `export_results()` route
   - `load_databricks_table()` route

2. **parse_json_data()** - Called by:
   - `dashboard()` route
   - `export_results()` route
   - `load_databricks_table()` route

3. **format_results_for_display()** - Called by:
   - `dashboard()` route
   - `export_results()` route

4. **databricks.list_available_tables()** - Called by:
   - `dashboard()` route
   - `export_results()` route

---

## Error Handling Flow

```
Route Handler
    │
    ├─> try:
    │   ├─> Databricks Operations
    │   │   └─> Exception raised
    │   ├─> Data Parsing
    │   │   └─> validation_errors collected
    │   └─> Template Rendering
    │
    └─> except Exception as e:
        ├─> traceback.print_exc()
        ├─> render_template('error.html', error=str(e))
        └─> return with status code (400, 404, 500)
```

---

## Configuration Flow

```
.env file
    │
    ├─> load_dotenv()
    │
    ├─> ENABLE_DATABRICKS
    │   └─> databricks_enabled
    │
    ├─> DATABRICKS_HOST
    ├─> DATABRICKS_TOKEN
    ├─> DATABRICKS_HTTP_PATH
    ├─> DATABRICKS_CATALOGS
    ├─> DATABRICKS_SCHEMAS
    ├─> DATABRICKS_TABLE_PATTERN
    ├─> DATABRICKS_CACHE_DURATION
    │   └─> DatabricksConnector(...)
    │
    └─> FLASK_SECRET_KEY
        └─> app.secret_key
```

---

## Execution Timeline (Typical User Journey)

### Scenario: User views provider verification dashboard

```
Time  │ Action
──────┼─────────────────────────────────────────────────────────
T+0s  │ User navigates to /
      │ ├─> index() route handler
      │ ├─> databricks.load_table_data('csv_upload_details')
      │ │   └─> SQL query executed
      │ └─> render upload_list.html
──────┼─────────────────────────────────────────────────────────
T+1s  │ User clicks on csv_file_id link
      │ └─> Redirects to /dashboard?csv_file_id=XXX
──────┼─────────────────────────────────────────────────────────
T+2s  │ dashboard() route handler
      │ ├─> databricks.list_available_tables()
      │ │   ├─> Check cache (5 min TTL)
      │ │   └─> Query information_schema if cache miss
      │ ├─> Search tables for csv_file_id
      │ │   └─> Multiple load_table_data() calls (with limit=1)
      │ ├─> Found table, load all data
      │ │   └─> databricks.load_table_data(table, csv_file_id)
      │ ├─> parse_json_data(table_data)
      │ │   └─> Parse ~100-1000 records
      │ ├─> format_results_for_display()
      │ │   └─> Format each record for display
      │ └─> render dashboard.html
──────┼─────────────────────────────────────────────────────────
T+3s  │ Page rendered, user interacts with filters (client-side JS)
──────┼─────────────────────────────────────────────────────────
T+30s │ User clicks "Export CSV"
      │ └─> Redirects to /export?csv_file_id=XXX
──────┼─────────────────────────────────────────────────────────
T+31s │ export_results() route handler
      │ ├─> Same data loading as dashboard
      │ ├─> pd.DataFrame(formatted_results)
      │ ├─> df.to_csv()
      │ └─> send_file() downloads CSV
──────┴─────────────────────────────────────────────────────────
```

---

## Performance Considerations

### Caching Strategy
- **Table List Cache**: 5-minute TTL (configurable)
- **Cache Invalidation**: Force refresh with `force_refresh=True`

### Database Query Optimization
- **Limit queries**: Used when searching for csv_file_id (limit=1)
- **Full data load**: No limit when displaying dashboard
- **WHERE clause**: Filters by csv_file_id to reduce data transfer

### Potential Bottlenecks
1. **list_available_tables()**: Queries all tables in schema
2. **Dashboard search loop**: Multiple queries to find correct table
3. **Data parsing**: Processes all records in Python
4. **Export**: Creates temporary CSV file on disk

---

## Future Extensibility Points

### Backend Integration (backend_connector.py)
- Currently stubbed, ready for:
  - Databricks Jobs API integration
  - Custom REST API endpoints
  - Delta table writes

### Upload Functionality (file_handler.py)
- Prepared but not currently used
- Ready for CSV/Excel upload feature

### Additional Routes
- Easy to add new Flask routes following existing patterns
- Template inheritance via base.html

---

## Summary

This Healthcare Provider Directory application follows a clean MVC-style architecture:

- **Controllers**: Flask route handlers in app.py
- **Models**: Data access via DatabricksConnector
- **Views**: Jinja2 templates (dashboard.html, upload_list.html, etc.)
- **Utilities**: Data formatting and file handling helpers

The call graph demonstrates:
- Clear separation of concerns
- Reusable utility functions
- Consistent error handling
- Extensibility for future features

**Key Entry Points**:
1. **User Interface**: Flask routes (`/`, `/dashboard`, `/export`)
2. **Data Access**: DatabricksConnector methods
3. **Data Processing**: data_formatter functions

**Main Data Pipeline**:
```
Databricks Table → load_table_data() → parse_json_data() → format_results_for_display() → HTML Template
```
