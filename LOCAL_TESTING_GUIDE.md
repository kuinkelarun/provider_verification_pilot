# 🧪 Local Testing Guide

## Quick Start - Test in 5 Minutes

### Step 1: Install Dependencies
```bash
# Open PowerShell in your project directory
cd "c:\Users\arun.kuinkel\OneDrive - Accenture\AFS-GenWizard Deployment\Applications\AI Pilot - Healthcare Provider Directory"

# Install required packages
pip install -r requirements.txt
```

### Step 2: Verify Setup (Optional but Recommended)
```bash
# Run the automated setup verification
.\test_setup.bat
```

### Step 3: Start the Application
```bash
# Start Flask development server
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 4: Open in Browser
Navigate to: **http://localhost:5000**

---

## 📋 Detailed Testing Checklist

### 1️⃣ Test Upload Functionality

**A. Download Sample File**
1. Go to http://localhost:5000
2. Scroll to instructions section
3. Click "📥 Download Sample File"
4. Save `sample_verification_results.csv`

**B. Upload the Sample File**
1. Drag and drop the CSV onto the upload zone (or click "Browse Files")
2. Wait for file preview
3. Click "Process File"
4. Wait for redirect to dashboard

**Expected Result:**
- ✅ File uploads successfully
- ✅ Redirects to dashboard with data
- ✅ Shows 20 providers from sample file

---

### 2️⃣ Test Dashboard Display

**Check Metrics Cards:**
- Total Providers: Should show 20
- Verified: Should show count of verified providers
- Needs Review: Should show count of needs_review
- Failed: Should show count of failed

**Check Table:**
- ✅ All 20 providers displayed
- ✅ Status badges colored correctly (green=verified, yellow=review, red=failed)
- ✅ Confidence scores show as progress bars
- ✅ Address changes highlighted (if any)
- ✅ Sources displayed with count

---

### 3️⃣ Test All Filters

**A. Search Filter**
```
Test 1: Type "Sarah" → Should show Dr. Sarah Johnson
Test 2: Type "1234567890" → Should show provider with that NPI
Test 3: Type "Boston" → Should show Boston providers
```

**B. File Filter**
```
Test 1: Should show "All Files" selected by default
Test 2: Upload a second file
Test 3: Switch between files using dropdown
Test 4: Select "All Files" to see combined data
```

**C. Status Filter**
```
Test 1: Select "✓ Verified" → Shows only verified providers
Test 2: Select "⚠ Needs Review" → Shows only needs_review
Test 3: Select "✗ Failed" → Shows only failed providers
Test 4: Select "All Statuses" → Shows all
```

**D. Confidence Filter**
```
Test 1: Select "High (>80%)" → Shows only providers with >80% confidence
Test 2: Select "Medium (50-80%)" → Shows 50-80% confidence
Test 3: Select "Low (<50%)" → Shows <50% confidence
Test 4: Select "All Confidence Levels" → Shows all
```

**E. City Filter**
```
Test 1: Dropdown should populate with unique cities
Test 2: Select a city (e.g., "Boston") → Shows only Boston providers
Test 3: Select "All Cities" → Shows all
```

**F. ZIP Code Filter**
```
Test 1: Type "02115" → Shows providers with that ZIP
Test 2: Type "021" → Shows all ZIPs starting with 021
Test 3: Clear field → Shows all
```

**G. Combine Filters**
```
Test: Apply multiple filters simultaneously
Example: City="Boston" + Status="verified" + Confidence="High"
Expected: Shows only Boston providers that are verified with high confidence
```

**H. Reset Filters**
```
Test: Click "Reset Filters" button
Expected: All filters return to default values, all data displayed
```

---

### 4️⃣ Test Sorting

Click each column header to test sorting:
```
✅ Status → Sorts alphabetically (failed, needs_review, verified)
✅ Provider Name → Sorts alphabetically
✅ NPI → Sorts numerically
✅ Address → Sorts alphabetically
✅ Specialty → Sorts alphabetically
✅ Confidence → Sorts by percentage (0-100)
```

Click again to reverse sort order (▴/▾).

---

### 5️⃣ Test Pagination

```
Test 1: If >50 providers, check pagination controls
Test 2: Click "Next »" → Goes to next page
Test 3: Click "« Previous" → Goes to previous page
Test 4: Page info should show "Page X of Y"
```

---

### 6️⃣ Test Export Functionality

**A. Export All Data**
```
1. Select "All Files" in file filter
2. Click "📥 Export CSV" button
3. File downloads: "provider_data_export_all_YYYYMMDD_HHMMSS.csv"
4. Open CSV → Should contain all uploaded data
```

**B. Export Specific File**
```
1. Select a specific file in file filter
2. Click "📥 Export CSV" button
3. File downloads: "provider_data_export_{file_id}_YYYYMMDD_HHMMSS.csv"
4. Open CSV → Should contain only that file's data
```

**C. Export Filtered Data**
```
1. Apply filters (e.g., City="Boston", Status="verified")
2. Click "📥 Export CSV"
3. Open CSV → Should contain ALL data (export ignores client-side filters)
Note: Currently exports all data from selected file/files, not filtered subset
```

---

### 7️⃣ Test Multi-File Support

**Upload Second File:**
1. Create a second CSV with different providers:
   ```csv
   Provider Name,NPI,Address,City,State,ZIP Code,Specialty,Phone,Email,Confidence Score,Status,Sources,Discrepancies
   "Dr. Test Provider",9876543210,"999 Test St","Cambridge","MA","02139","General Practice","617-555-9999","test@example.com","88%","verified","NPPES",""
   ```
2. Save as `test_providers.csv`
3. Go to home (http://localhost:5000)
4. Upload the new file

**Test File Switching:**
```
Test 1: File filter dropdown now shows 2 files
Test 2: Select first file → Dashboard shows first file's data only
Test 3: Select second file → Dashboard shows second file's data only
Test 4: Select "All Files" → Dashboard shows combined data from both files
```

**Check Data Persistence:**
```
Test 1: Stop the Flask server (Ctrl+C)
Test 2: Restart: python app.py
Test 3: Go to http://localhost:5000/dashboard
Test 4: Verify both uploaded files still appear in file filter
Expected: Data persists across server restarts
```

---

### 8️⃣ Test Edge Cases

**A. Upload CSV with Missing Columns**
```
Create CSV without optional columns (e.g., no Email, no Phone)
Expected: Dashboard displays "N/A" or empty for missing fields
```

**B. Upload CSV with Column Name Variations**
```
Test variations:
- "provider_name" vs "Provider Name" vs "ProviderName"
- "confidence_score" vs "Confidence Score" vs "Score"
Expected: Parser handles all variations correctly
```

**C. Upload CSV with Different Confidence Formats**
```
Test formats:
- Percentage: "85%"
- Decimal: "0.85"
- Plain number: "85"
Expected: All converted to 0-100 scale correctly
```

**D. Upload CSV with Different Status Values**
```
Test values:
- "Verified" vs "verified" vs "VERIFIED"
- "Needs Review" vs "needs_review" vs "NEEDS_REVIEW"
Expected: All normalized to lowercase with underscores
```

**E. Upload Empty CSV**
```
Upload CSV with only headers, no data rows
Expected: Error message or empty dashboard (no crash)
```

**F. Upload Very Large File**
```
Create CSV with 1000+ providers
Expected: Loads successfully, pagination works, filtering responsive
```

---

### 9️⃣ Test Error Handling

**A. Missing Required Columns**
```
Upload CSV without "Provider Name" or "NPI"
Expected: Error message explaining required columns
```

**B. Invalid File Type**
```
Try uploading .txt or .pdf file
Expected: Error message "Invalid file type"
```

**C. File Too Large**
```
Try uploading file >50 MB
Expected: Error message "File too large"
```

**D. No Files Uploaded**
```
Navigate directly to http://localhost:5000/dashboard
Expected: Error page "No data found. Please upload a file first."
```

---

### 🔟 Test UI/UX

**Check Responsive Design:**
```
Test 1: Resize browser window
Expected: Layout adjusts, remains usable
```

**Check Visual Elements:**
```
✅ Colors: Blue for primary, green for verified, yellow for review, red for failed
✅ Icons: Status badges show ✓, ⚠, ✗ symbols
✅ Hover effects: Buttons change color on hover
✅ Loading states: Spinner shows during file processing
✅ Tooltips: Sources show full list on hover
```

**Check Accessibility:**
```
✅ All buttons have clear labels
✅ Form inputs have placeholders
✅ Error messages are clear and actionable
✅ Links are underlined or clearly styled
```

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Address already in use" (Port 5000 busy)
**Solution:**
```bash
# Option 1: Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Option 2: Change port in app.py
# Change: app.run(debug=True)
# To: app.run(debug=True, port=5001)
```

### Issue: CSS not loading (page looks unstyled)
**Solution:**
```bash
# Check static folder exists
dir static\css\style.css

# Clear browser cache
Ctrl+Shift+R (hard refresh)

# Check Flask console for 404 errors on static files
```

### Issue: Dashboard shows "No data found"
**Solution:**
```bash
# Check data_storage directory exists and has files
dir data_storage

# Check upload_history.json exists
type data_storage\upload_history.json

# If empty, upload a new file
```

### Issue: File upload fails silently
**Solution:**
```bash
# Check Flask console for error messages
# Verify uploads directory exists
dir uploads

# Check file size < 50 MB
# Check file format is CSV or Excel
```

---

## 📊 Test Data Templates

### Minimal Valid CSV
```csv
Provider Name,NPI
"Dr. Test Provider",1234567890
```

### Complete CSV (Recommended)
```csv
Provider Name,NPI,Address,City,State,ZIP Code,Specialty,Phone,Email,Confidence Score,Status,Sources,Discrepancies
"Dr. Sarah Johnson",1234567890,"123 Medical Plaza","Boston","MA","02115","Cardiology","617-555-0100","sjohnson@example.org","95%","verified","NPPES,CMS",""
"Dr. Michael Chen",1234567891,"456 Healthcare Blvd","Cambridge","MA","02138","Internal Medicine","617-555-0101","mchen@example.com","72%","needs_review","NPPES","Phone not confirmed"
"Dr. Failed Test",1234567892,"Not found","Boston","MA","02101","Unknown","","","25%","failed","","Provider not found"
```

### Test Edge Cases CSV
```csv
provider_name,npi,confidence_score,status
"Test Variations 1",1111111111,0.85,Verified
"Test Variations 2",2222222222,85%,NEEDS_REVIEW
"Test Variations 3",3333333333,85,failed
```

---

## ✅ Final Verification Checklist

Before considering testing complete, verify:

- [ ] Application starts without errors
- [ ] Sample CSV uploads successfully
- [ ] Dashboard displays data correctly
- [ ] All 8 filters work (search, file, status, confidence, city, zipcode, reset)
- [ ] Sorting works on all columns
- [ ] Pagination works (if >50 rows)
- [ ] Export downloads CSV file
- [ ] Multi-file support works (upload 2+ files)
- [ ] File switching works correctly
- [ ] Data persists after server restart
- [ ] UI looks correct (CSS loaded)
- [ ] No console errors in browser (F12 → Console)
- [ ] No errors in Flask console

---

## 🚀 Advanced Testing

### Performance Testing
```bash
# Test with large file (1000+ rows)
# Measure page load time
# Check filtering responsiveness
# Verify memory usage
```

### Browser Compatibility
```
Test in:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if available)
```

### Concurrent Users
```bash
# Open multiple browser tabs
# Upload different files simultaneously
# Check for conflicts
```

---

## 📝 Test Log Template

Use this to track your testing:

```
Date: ___________
Tester: ___________

[ ] Dependencies installed
[ ] Application starts
[ ] Upload works
[ ] Dashboard displays
[ ] Filters work (8/8)
[ ] Sorting works
[ ] Export works
[ ] Multi-file support
[ ] Data persistence
[ ] UI/CSS correct
[ ] No console errors

Issues Found:
1. ___________
2. ___________

Notes:
___________
```

---

## 🎓 Next Steps After Testing

Once local testing is complete:

1. **Document Issues**: Note any bugs or unexpected behavior
2. **Customize**: Adjust styling, filters, or features as needed
3. **Deploy**: Consider deployment options (see DEPLOYMENT.md)
4. **Production Data**: Test with your actual verification results
5. **User Training**: Share instructions with team members

---

**Happy Testing! 🎉**

Need help? Check:
- **README_V2.md** - Feature overview
- **QUICKSTART_V2.md** - Setup guide
- **ARCHITECTURE_CHANGES.md** - Technical details
