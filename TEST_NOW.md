# 🚀 QUICK START - Test in 2 Minutes!

## Option 1: Double-Click to Start (Easiest)

1. **Double-click**: `START.bat`
2. **Wait**: Installation completes (first time only)
3. **Open browser**: http://localhost:5000
4. **Done!** Dashboard is running

---

## Option 2: Manual Start (For troubleshooting)

### Step 1: Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

### Step 2: Start Server
```bash
python app.py
```

### Step 3: Open Browser
Navigate to: **http://localhost:5000**

---

## ✅ Verify It's Working

You should see:
1. **Upload Page** with drag-and-drop file zone
2. **Blue/white healthcare-themed UI** (means CSS is loaded ✓)
3. **Download Sample File** link in instructions

---

## 📥 Test with Sample Data

### Quick Test (30 seconds):
1. Click "**📥 Download Sample File**" on upload page
2. Drag the downloaded CSV onto upload zone
3. Click "**Process File**"
4. See dashboard with 20 providers!

### What You'll See:
- ✅ 20 providers displayed
- ✅ Summary metrics (verified, needs review, failed)
- ✅ Colorful status badges
- ✅ Filter controls (search, status, confidence, city, ZIP)
- ✅ Export button

---

## 🎨 Is CSS Working?

### You should see:
- ✅ Blue header with white text
- ✅ White cards with shadows
- ✅ Green "verified" badges
- ✅ Yellow "needs review" badges
- ✅ Red "failed" badges
- ✅ Blue buttons
- ✅ Styled dropdown filters

### If page looks plain (no colors):
1. Check browser console (F12) for CSS errors
2. Hard refresh: `Ctrl+Shift+R`
3. Verify file exists: `static\css\style.css`

---

## 🐛 Troubleshooting

### "Port 5000 already in use"
```bash
# Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or use different port - edit app.py line:
# app.run(debug=True, port=5001)
```

### "Module not found" errors
```bash
pip install flask pandas openpyxl xlrd
```

### Dashboard shows "No data found"
- Upload a CSV file first from home page
- Sample file available on upload page

---

## 📁 Test Files Location

- **Sample Data**: `static\sample_verification_results.csv`
- **Uploaded Files**: Saved to `data_storage\` (auto-created)
- **Temporary Uploads**: `uploads\` (auto-created)

---

## 📚 Full Documentation

After quick test, read:
- **LOCAL_TESTING_GUIDE.md** - Complete testing checklist
- **README_V2.md** - Full features and overview
- **QUICKSTART_V2.md** - Detailed setup guide

---

## ⚡ Expected Results

### Upload Page
![Upload page should show drag-and-drop zone with blue styling]

### Dashboard
![Dashboard should show table with colored badges and filters]

### Summary Metrics
- Total: 20
- Verified: ~12-15 (green)
- Needs Review: ~3-5 (yellow)
- Failed: ~1-2 (red)

---

## 🎯 Next Steps

1. ✅ Verify dashboard displays correctly
2. ✅ Test all filters (search, status, city, etc.)
3. ✅ Upload a second CSV to test multi-file support
4. ✅ Test export functionality
5. ✅ Review full testing guide: `LOCAL_TESTING_GUIDE.md`

---

**Server Running?** Look for:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Ready to Test?** 
1. Go to: http://localhost:5000
2. Download sample file
3. Upload and explore!

🎉 **Enjoy your dashboard!**
