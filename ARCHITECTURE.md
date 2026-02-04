# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│  (Chrome, Firefox, Safari, Edge)                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP/HTTPS
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    FLASK WEB APPLICATION                         │
│                        (app.py)                                  │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │  Upload Route  │  │ Dashboard Route│  │  Export Route   │  │
│  │   POST /upload │  │ GET /dashboard │  │ GET /export     │  │
│  └────────┬───────┘  └────────┬───────┘  └────────┬────────┘  │
│           │                   │                   │            │
│           └───────────────────┴───────────────────┘            │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                              │
        ▼                                              ▼
┌───────────────────┐                         ┌────────────────────┐
│   UTILS MODULE    │                         │   STATIC ASSETS    │
│                   │                         │                    │
│ • file_handler    │                         │  • style.css       │
│ • backend_connect │                         │  • dashboard.js    │
│ • data_formatter  │                         │  • (images)        │
└─────────┬─────────┘                         └────────────────────┘
          │
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌──────────────────────┐
│ MOCK   │  │  DATABRICKS BACKEND  │
│ DATA   │  │  (Phase 2)           │
│ MODE   │  │                      │
│        │  │  • Jobs API          │
│ ✅ Now │  │  • REST API          │
│        │  │  • Delta Tables      │
└────────┘  └──────────────────────┘
```

## Data Flow

### Phase 1: Mock Mode (Current)

```
User Upload
    │
    ├─> Flask receives file
    │       │
    │       ├─> Validate file type/size
    │       ├─> Save to disk
    │       ├─> Read CSV/Excel
    │       │
    │       └─> Generate Mock Results
    │               │
    │               ├─> 60% Verified
    │               ├─> 20% Needs Review
    │               ├─> 15% With Changes
    │               └─> 5% Failed
    │
    └─> Store in session
            │
            └─> Display Dashboard
                    │
                    ├─> Summary Cards
                    ├─> Filters
                    ├─> Results Table
                    └─> Export CSV
```

### Phase 2: Production Mode (Future)

```
User Upload
    │
    ├─> Flask receives file
    │       │
    │       ├─> Validate file type/size
    │       ├─> Save to disk
    │       │
    │       └─> Trigger Databricks Backend
    │               │
    │               ├─> AI Verification
    │               │     (Gemini LLM)
    │               │
    │               ├─> Web Scraping
    │               │     (NPPES, Medical Boards)
    │               │
    │               ├─> Confidence Scoring
    │               │     (Algorithm)
    │               │
    │               └─> Write to Delta Table
    │
    ├─> Poll for completion
    │
    └─> Fetch results from backend
            │
            └─> Display Dashboard
                    │
                    ├─> Real verification status
                    ├─> Actual confidence scores
                    ├─> True data sources
                    └─> Production results
```

## Component Breakdown

### Frontend Layer

```
┌─────────────────────────────────────────────┐
│           HTML Templates                    │
│                                             │
│  • base.html      - Layout & header        │
│  • upload.html    - File upload screen     │
│  • dashboard.html - Results display        │
│  • error.html     - Error handling         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           CSS (style.css)                   │
│                                             │
│  • Color palette & variables               │
│  • Component styles (cards, tables, etc)   │
│  • Responsive design (mobile/desktop)      │
│  • Animations & transitions                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│        JavaScript (dashboard.js)            │
│                                             │
│  • Real-time filtering                     │
│  • Client-side search                      │
│  • Table sorting                           │
│  • Pagination logic                        │
└─────────────────────────────────────────────┘
```

### Backend Layer

```
┌─────────────────────────────────────────────┐
│            Flask Application                │
│                                             │
│  Routes:                                    │
│  • GET  /              - Upload page       │
│  • POST /upload        - Handle upload     │
│  • GET  /dashboard/:id - Show results      │
│  • GET  /export/:id    - Download CSV      │
│  • POST /api/filter    - Filter results    │
│  • GET  /health        - Health check      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              Utils Module                   │
│                                             │
│  file_handler.py:                          │
│  • validate_file()                         │
│  • handle_file_upload()                    │
│                                             │
│  backend_connector.py:                     │
│  • process_batch()                         │
│  • get_batch_results()                     │
│                                             │
│  data_formatter.py:                        │
│  • generate_mock_results()                 │
│  • format_results_for_display()            │
└─────────────────────────────────────────────┘
```

## Database/Storage

### Current (Phase 1)
```
┌─────────────────────┐
│   Flask Session     │
│   (In-Memory)       │
│                     │
│  • Temporary        │
│  • Per-session      │
│  • Lost on restart  │
└─────────────────────┘
```

### Future (Phase 2)
```
┌─────────────────────────────────────┐
│      Databricks Delta Tables        │
│                                     │
│  • provider_verification_input      │
│    (uploaded files)                 │
│                                     │
│  • provider_verification_results    │
│    (AI verification output)         │
│                                     │
│  • Persistent storage               │
│  • Audit trail                      │
│  • Query-able via SQL               │
└─────────────────────────────────────┘
```

## Integration Points

### Current State
```
Flask App <──> Mock Data Generator
                    │
                    └──> Realistic fake results
```

### Target State (Phase 2)
```
                    ┌─> Databricks Jobs API
                    │
Flask App <─────────┼─> REST API Endpoint
                    │
                    └─> Delta Table Queries
                            │
                            └─> Spark/PySpark
```

## Deployment Architecture

### Local Development
```
Developer Machine
    │
    ├─> Python 3.10+
    ├─> Flask server (localhost:8080)
    └─> Browser testing
```

### Databricks Apps (Production)
```
┌─────────────────────────────────────────┐
│      Databricks Workspace              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Flask App Container            │  │
│  │   (Managed by Databricks)        │  │
│  │                                  │  │
│  │   • Auto-scaling                 │  │
│  │   • Load balancing               │  │
│  │   • SSL/TLS                      │  │
│  │   • Authentication               │  │
│  └──────────────────────────────────┘  │
│              │                          │
│              ├─> Spark Cluster          │
│              ├─> Delta Tables           │
│              └─> Unity Catalog          │
└─────────────────────────────────────────┘
                │
                ▼
    Users access via HTTPS URL
```

## Security Architecture

```
┌────────────────────────────────────────────┐
│         Security Layers                    │
│                                            │
│  1. Input Validation                       │
│     • File type checking                   │
│     • Size limits                          │
│     • Column validation                    │
│                                            │
│  2. File Handling                          │
│     • Secure filename sanitization         │
│     • Temporary storage                    │
│     • Automatic cleanup                    │
│                                            │
│  3. Authentication (Phase 3)               │
│     • OAuth integration                    │
│     • Role-based access                    │
│     • Session management                   │
│                                            │
│  4. Data Protection                        │
│     • No PII stored                        │
│     • Encrypted in transit (HTTPS)         │
│     • Environment variable secrets         │
└────────────────────────────────────────────┘
```

## Scalability Considerations

### Current Capacity
- **Files**: Up to 50MB (~50,000 providers)
- **Concurrent users**: 10-20 (single instance)
- **Response time**: <2 seconds for dashboard load

### Future Scaling
```
Load Balancer
    │
    ├─> Flask Instance 1
    ├─> Flask Instance 2
    ├─> Flask Instance 3
    └─> Flask Instance N
            │
            └─> Shared Delta Table Backend
```

## Monitoring & Observability

```
┌─────────────────────────────────────────┐
│         Monitoring Stack                │
│                                         │
│  Application Logs                       │
│  ├─> Flask debug logs                  │
│  ├─> Error tracking                    │
│  └─> Access logs                       │
│                                         │
│  Metrics (Future)                       │
│  ├─> Upload volume                     │
│  ├─> Processing time                   │
│  ├─> Error rates                       │
│  └─> User activity                     │
│                                         │
│  Alerts (Future)                        │
│  ├─> High error rate                   │
│  ├─> Performance degradation           │
│  └─> Backend connectivity issues       │
└─────────────────────────────────────────┘
```

## Technology Stack Summary

### Core Technologies
- **Backend**: Python 3.10+, Flask 3.0
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Processing**: Pandas 2.1+
- **File Handling**: OpenPyXL, XLRD

### Infrastructure
- **Hosting**: Databricks (Azure)
- **Storage**: Delta Lake (future)
- **Compute**: Databricks Clusters

### Development Tools
- **Version Control**: Git
- **Package Management**: pip
- **Documentation**: Markdown

## Performance Characteristics

### Response Times (Mock Mode)
```
Operation                Time
─────────────────────────────────
Upload 1,000 rows       < 2s
Upload 10,000 rows      < 5s
Dashboard load          < 1s
Search/filter           < 100ms
Sort column            < 200ms
Export to CSV          < 2s
```

### Resource Usage
```
Memory: ~200MB (idle)
        ~500MB (processing 10k rows)
        
CPU:    Low (mostly I/O bound)
        
Disk:   Minimal (temp file storage)
```

---

## Quick Reference

**Entry Point**: `app.py`
**Frontend**: `templates/` + `static/`
**Backend Logic**: `utils/`
**Configuration**: `.env` (create from `.env.example`)
**Documentation**: All `.md` files
**Sample Data**: `sample_providers.csv`

---

**This architecture is designed to be:**
- ✅ Simple to understand
- ✅ Easy to maintain
- ✅ Ready to scale
- ✅ Secure by default
- ✅ Production-ready
