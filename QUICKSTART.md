# Quick Start Guide - Provider Verification Dashboard

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (1 minute)

```bash
# Open terminal in project directory
pip install -r requirements.txt
```

### Step 2: Run the Application (1 minute)

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:8080
 * Running on http://127.0.0.1:8080
```

### Step 3: Open in Browser (1 minute)

Navigate to: `http://localhost:8080`

### Step 4: Test with Sample Data (2 minutes)

1. **Download the template** from the upload page, OR
2. **Create a CSV file** named `sample_providers.csv`:

```csv
Provider Name,NPI,Address,City,State,ZIP Code,Specialty,Phone
Dr. Sarah Johnson,1234567890,123 Medical Plaza Dr,Boston,MA,02115,Cardiology,617-555-0100
Dr. Michael Chen,2345678901,456 Healthcare Blvd,Cambridge,MA,02139,Pediatrics,617-555-0200
Dr. Emily Rodriguez,3456789012,789 Hospital Way,Brookline,MA,02445,Internal Medicine,617-555-0300
Dr. James Williams,4567890123,321 Clinic Street,Newton,MA,02458,Orthopedic Surgery,617-555-0400
Dr. Linda Martinez,5678901234,654 Doctor Lane,Somerville,MA,02143,Obstetrics & Gynecology,617-555-0500
Dr. Robert Taylor,6789012345,987 Health Center Ave,Waltham,MA,02451,Emergency Medicine,617-555-0600
Dr. Patricia Anderson,7890123456,147 Medical Arts Blvd,Quincy,MA,02169,Psychiatry,617-555-0700
Dr. David Thompson,8901234567,258 Practice Parkway,Medford,MA,02155,Family Medicine,617-555-0800
Dr. Jennifer Garcia,9012345678,369 Provider Plaza,Malden,MA,02148,Dermatology,617-555-0900
Dr. Christopher Lee,1122334455,741 Specialist Street,Everett,MA,02149,Radiology,617-555-1000
```

3. **Upload the file** to the dashboard
4. **View the results** with mock verification data

### Step 5: Explore the Dashboard

✅ **What Works Now (Mock Mode)**:
- File upload with validation
- Beautiful dashboard display
- Realistic mock verification results
- Search and filter functionality
- Sorting by column
- Pagination for large datasets
- CSV export

⏳ **What Needs Backend Integration**:
- Real AI-powered verification
- Actual confidence scoring
- True data source validation

## 🎯 Expected Behavior

### Upload Screen
- Drag-and-drop or click to browse
- File preview showing first rows
- Validation messages if file format is wrong

### Dashboard
- Summary cards showing verification stats
- Filterable table with sortable columns
- Color-coded status badges:
  - 🟢 Green = Verified (high confidence)
  - 🟡 Yellow = Needs Review (medium confidence)
  - 🔴 Red = Failed (low confidence)

## 🔧 Configuration

### Current Mode: MOCK DATA

The app is currently in **mock data mode** for development:

```python
# In app.py, line 19:
MOCK_DATA_MODE = True  # ← Currently enabled
```

**What this means:**
- Uploads work normally
- Backend verification is simulated
- Results are realistic but fake
- Perfect for UI testing and stakeholder demos

### Switching to Production Mode

When your backend is ready:

1. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Databricks credentials
   ```

2. **Implement backend connection** in `utils/backend_connector.py`

3. **Disable mock mode**:
   ```python
   # In app.py:
   MOCK_DATA_MODE = False
   ```

4. **Restart the application**

## 📊 Sample Data Breakdown

The sample CSV includes:
- 10 providers
- All required fields (Provider Name, NPI)
- Optional fields (Address, City, State, ZIP, Specialty, Phone)

When processed, you'll see:
- ~60% verified (high confidence)
- ~20% needs review (medium confidence)
- ~15% verified with changes (address corrections)
- ~5% failed (not found)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# If port 8080 is busy, edit app.py line 243:
app.run(host='0.0.0.0', port=8081, debug=True)
```

### Module Not Found
```bash
# Reinstall dependencies:
pip install --upgrade -r requirements.txt
```

### File Upload Fails
- Check file size (<50MB)
- Verify file format (CSV, XLSX, XLS)
- Ensure columns include "Provider Name" and "NPI"

### Dashboard Not Loading
- Check browser console for errors
- Clear browser cache
- Verify static files are present in `static/` folder

## 📱 Accessing from Other Devices

To access from other devices on your network:

1. Find your local IP address:
   ```bash
   # Windows:
   ipconfig
   
   # Mac/Linux:
   ifconfig
   ```

2. Access from other device:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

## 🎨 Customization

### Change Page Title
Edit `templates/base.html` line 6

### Change Color Scheme
Edit CSS variables in `static/css/style.css` lines 11-23

### Adjust Rows Per Page
Edit `static/js/dashboard.js` line 7:
```javascript
const rowsPerPage = 50;  // Change to desired number
```

## ✅ Success Checklist

- [ ] Application starts without errors
- [ ] Upload page displays correctly
- [ ] Can upload CSV file
- [ ] Dashboard shows mock results
- [ ] Filters and search work
- [ ] Sorting works on all columns
- [ ] Pagination controls work
- [ ] Export CSV downloads file

## 📞 Next Steps

1. **Demo to stakeholders** - Get feedback on UI/UX
2. **Collect backend requirements** - Interface details, data formats
3. **Implement backend integration** - Connect to real verification system
4. **Test with real data** - Validate with production data
5. **Deploy to Databricks** - Move to production environment

---

**🎉 You're ready to go! Upload a file and explore the dashboard.**
