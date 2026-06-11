# Quick Start Guide

## Fastest Way to Get Started

### Windows
1. Double-click **`run.bat`**
2. Wait for setup check
3. App launches automatically

### Mac / Linux
```bash
chmod +x run.sh
./run.sh
```

---

## Manual Setup (if needed)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py
```

---

## First Time Usage

### Add Your First Student
1. Click **"Add Student"** button in sidebar
2. Fill in:
   - Roll Number (required)
   - Full Name (required)
   - Email, Phone, Class (optional)
   - Marks for 5 subjects (0-100)
3. Click **"Save Student Record"**

### View Results
1. Go to **"Results"** tab
2. Select a student from the dropdown
3. View their report card with grade and status

### Export Data
- **"Export CSV Data"** → Download full class rankings as Excel
- **"Generate Reports"** → Create PDF report cards for all students

---

## Features

✅ **Add/Edit/Delete Students**  
✅ **Calculate marks automatically**  
✅ **View reports & rankings**  
✅ **Export to PDF & CSV**  
✅ **Charts & statistics dashboard**  
✅ **Dark theme UI**  

---

## Troubleshooting

**Error: Module not found**
```
Run: python check_setup.py
Then: pip install -r requirements.txt
```

**Charts not showing?**
```
Install: pip install matplotlib
```

**PDF export not working?**
```
Install: pip install fpdf2
```

---

**Questions?** Check the full README.md for detailed documentation.
