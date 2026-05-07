# GitHub Setup & Build Instructions

## 1. Create GitHub Repository

### Step 1: Create a Repository on GitHub
1. Go to [GitHub.com](https://github.com)
2. Click the **+** icon in the top right → **New repository**
3. Name it: `SalesOrderAnalyzer`
4. Add description: `Sales Order Analysis Tool with GUI for Windows`
5. Choose **Public** or **Private** (as needed)
6. Check **Add a README file**
7. Click **Create repository**

### Step 2: Clone & Setup Locally
```bash
# Clone the repository (replace USERNAME with your GitHub username)
git clone https://github.com/USERNAME/SalesOrderAnalyzer.git
cd SalesOrderAnalyzer

# Copy your project files into this directory
```

## 2. Add Project Files to Git

```bash
# Stage all files
git add .

# Commit with a message
git commit -m "Initial commit: Sales Order Analyzer with GUI"

# Push to GitHub
git push origin main
```

## 3. Build Windows .exe

### On a Windows Machine:

#### Option A: Portable Python (Simplest)
1. Download portable Python from [WinPython](https://github.com/winpython/winpython/releases)
2. Extract to `C:\PortablePython`
3. Open Command Prompt in that folder:
```bash
cd C:\PortablePython
Scripts\python.exe -m pip install -r "C:\path\to\requirements.txt"
cd "C:\path\to\project"
Scripts\python.exe -m PyInstaller SO_analysis.spec
```

#### Option B: Standard Python
1. Install Python 3.9+ from [python.org](https://www.python.org/downloads)
2. Open Command Prompt:
```bash
cd "C:\path\to\project"
pip install -r requirements.txt
pyinstaller SO_analysis.spec
```

### Result:
- Executable will be: `dist\SalesOrderAnalyzer.exe`
- Copy this file to your desired location
- Users can run it directly without Python installed

## 4. Upload Built Executable to GitHub (Releases)

### Create a Release with the .exe

1. Go to your repository on GitHub
2. Click **Releases** (on the right sidebar)
3. Click **Create a new release**
4. Tag version: `v2.1` (or your version)
5. Release title: `Sales Order Analyzer v2.1`
6. Add description:
```markdown
## Sales Order Analyzer v2.1

Standalone Windows application for analyzing sales order data.

### Features
- GUI interface for easy file selection
- Lead time calculation with MSQ logic
- Bottleneck analysis
- Excel report generation

### Requirements
- Windows 7 or later
- No Python installation needed!

### Usage
1. Download `SalesOrderAnalyzer.exe`
2. Run the executable
3. Select your input files
4. Click "Run Analysis"

### Files Needed
- Sales Order Excel file
- Location mapping file
- Lead Times reference file (default path: `Lead Time file.xlsx`)
```

7. Click **Attach binaries** or drag `SalesOrderAnalyzer.exe` into the upload area
8. Click **Publish release**

## 5. Share the Download Link

Users can now download from:
```
https://github.com/USERNAME/SalesOrderAnalyzer/releases/download/v2.1/SalesOrderAnalyzer.exe
```

## 6. GitHub Repository Structure

```
SalesOrderAnalyzer/
├── SO_analysis.py          # Main Python script with GUI
├── SO_analysis.spec        # PyInstaller configuration
├── requirements.txt        # Python dependencies
├── README.md              # User guide
├── GITHUB_SETUP.md        # This file
├── .gitignore            # Git ignore file
└── dist/                 # Built executable (generated)
    └── SalesOrderAnalyzer.exe
```

## 7. Update Workflow

When you make updates:

1. Update code locally
2. Test locally: `python SO_analysis.py`
3. Commit & push:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

4. Rebuild on Windows:
```bash
pyinstaller SO_analysis.spec
```

5. Create new release with updated .exe file

## Troubleshooting

**"git not found"**: 
- Install Git from [git-scm.com](https://git-scm.com/download/win)

**Build fails on Windows**:
- Ensure Python 3.9+ is installed
- Run: `pip install --upgrade pyinstaller`
- Try building with: `pyinstaller --onefile SO_analysis.py`

**Executable won't run**:
- Right-click → Run as Administrator
- Check antivirus isn't blocking it
- Try building without the .spec file

## Alternative: Automated Builds with GitHub Actions

You can automate the Windows .exe build using GitHub Actions CI/CD (Advanced):
- See `.github/workflows/` directory for action files
- Automatically builds .exe on every release
- Makes distribution much easier
