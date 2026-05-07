# Quick Start Guide

## For End Users (Windows)

### Running the Application

1. **Download** `SalesOrderAnalyzer.exe` from GitHub Releases
2. **Double-click** to run (no installation needed!)
3. **Select your files**:
   - Sales Order Excel file
   - Location mapping Excel file
   - Lead Times file path
4. **Click "Run Analysis"**
5. **View the results** in the generated Excel file

## For Developers (Building the .exe)

### Prerequisites
- Windows 10 or later
- Python 3.9+ (from [python.org](https://www.python.org/downloads))
- Git (from [git-scm.com](https://git-scm.com))

### Step 1: Clone Repository
```bash
git clone https://github.com/USERNAME/SalesOrderAnalyzer.git
cd SalesOrderAnalyzer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Build Executable
**Option A - Using provided batch script:**
```bash
build.bat
```

**Option B - Manual build:**
```bash
pyinstaller SO_analysis.spec
```

### Step 4: Find Your Executable
```
dist/SalesOrderAnalyzer.exe
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "File not found" | Check file paths, use absolute paths if files are in different directories |
| Analysis fails | Ensure Excel files have required columns and correct date format |
| .exe won't run | Right-click → Run as Administrator, or check antivirus |
| "No module" error | Run `pip install -r requirements.txt` |

## File Format Requirements

### Sales Order File (.xlsx)
```
Required Columns:
- Tag No
- Item Description  
- Qty
- OA Date (format: DD MMM YYYY HH:MM:SS)
- Cost Approval Remark (contains DD MMM YYYY HH:MM:SS ...)
- Account Remark (contains DD MMM YYYY HH:MM:SS ...)
- PPC Remark (contains DD MMM YYYY HH:MM:SS ...)
- Dispatch Remark (contains DD MMM YYYY HH:MM:SS ...)
```

### Location File (.xlsx)
```
Required Columns:
- Item Categories (or Item Group or Item Category)
- Location

Example:
Item Categories | Location
===============|==========
Pipes          | Warehouse A
Valves         | Warehouse B
Fittings       | Warehouse A
```

### Lead Times File (.xlsx)
```
Required Columns:
- Item Description
- Lead Time (format: "5" or "2 to 3 days" or "5 days")
- Item Categories (or Item Group or Item Category)

Optional Columns:
- Confirmed MSQ if any
- Batch production quantity per day
```

## Output

The analysis generates an Excel file containing:
- All original order data
- Extracted timestamps from remarks
- Lead time calculations
- Item locations
- Time differences between processing stages
- Bottleneck identification
- Department-wise delay analysis

## For Support

1. Check README.md for detailed documentation
2. See GITHUB_SETUP.md for build troubleshooting
3. Verify all input files match the format requirements
