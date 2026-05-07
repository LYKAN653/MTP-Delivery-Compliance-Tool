# Complete Setup Guide: From Mac to Windows .exe Distribution

## 📋 Overview

You now have a complete Sales Order Analyzer application with:
- ✅ Professional GUI interface
- ✅ Windows .exe build capability
- ✅ GitHub repository structure
- ✅ All documentation

This guide will walk you through pushing to GitHub and building the Windows executable.

---

## 🚀 Step 1: Push to GitHub (On Mac)

### 1a. Create GitHub Account (if you don't have one)
- Go to [GitHub.com](https://github.com)
- Sign up with your email
- Verify email address

### 1b. Create New Repository
1. Click **+** (top right) → **New repository**
2. Repository name: `SalesOrderAnalyzer`
3. Description: `Sales Order Analysis Tool with GUI for Windows`
4. Visibility: **Public** (so anyone can download) or **Private** (restricted)
5. Click **Create repository**
6. **DO NOT** initialize with README (we already have files)

### 1c. Copy Your GitHub Repository URL
- You'll see a URL like: `https://github.com/YOUR_USERNAME/SalesOrderAnalyzer.git`
- Copy this URL

### 1d. Initialize Git on Mac

Open Terminal and run:

```bash
# Navigate to your project folder
cd "/Users/Aryan.Kadam/Library/CloudStorage/OneDrive-SharedLibraries-DahotreGroup/Engagements_04 - MTP - MTP/2. Engagement/1. TDA/Objectives/Delivery Compliance/Delivery Compliance tool"

# Check if git is already initialized
ls -la | grep ".git"

# If .git folder exists, skip to 1e
# If not, initialize git:
git init

# Configure git with your GitHub account
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 1e. Add Files and Push

```bash
# Add all files
git add .

# Check what's being added
git status

# Commit the changes
git commit -m "Initial commit: Sales Order Analyzer with GUI v2.1"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/SalesOrderAnalyzer.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main

# Enter your GitHub username and password
# (or use personal access token if 2FA is enabled)
```

### 1f. Verify on GitHub
- Go to your GitHub repository
- You should see all your files uploaded!

---

## 💻 Step 2: Build Windows .exe (On Windows Machine)

### Option A: Using Build Script (Easiest)

1. Go to your GitHub repository on GitHub.com
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file
4. Open Command Prompt in the extracted folder
5. Run: `build.bat`
6. Wait for build to complete
7. Your .exe will be in: `dist\SalesOrderAnalyzer.exe`

### Option B: Manual Build

1. Download and extract repository (as above)
2. Install Python 3.9+ from [python.org](https://www.python.org/downloads)
3. Open Command Prompt in project folder
4. Run:
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller SO_analysis.spec

# Your .exe is now in: dist\SalesOrderAnalyzer.exe
```

### Option C: Using Portable Python (No Installation)

1. Download WinPython from [GitHub](https://github.com/winpython/winpython/releases)
2. Extract to a folder (e.g., `C:\PortablePython`)
3. Open Command Prompt
4. Run:
```bash
cd C:\PortablePython
Scripts\python.exe -m pip install "path\to\requirements.txt"
cd "path\to\project"
Scripts\python.exe -m pyinstaller SO_analysis.spec
```

---

## 📦 Step 3: Upload .exe to GitHub Releases

### 3a. Create Release

1. Go to your GitHub repository
2. Click **Releases** (on the right, or scroll down)
3. Click **Create a new release**

### 3b. Create Release Details

**Tag version:** `v2.1`

**Release title:** `Sales Order Analyzer v2.1`

**Description:**
```markdown
## Sales Order Analyzer v2.1

Standalone Windows application for analyzing sales order data.

### 🎯 Features
- GUI interface for easy file selection
- Lead time calculation with MSQ logic
- Bottleneck analysis
- Excel report generation
- No Python installation needed!

### ✅ Requirements
- Windows 7 or later
- No software installation required
- 3 Excel files (Orders, Location, Lead Times)

### 📥 Download
Download `SalesOrderAnalyzer.exe` below

### 🚀 Usage
1. Download the .exe file
2. Double-click to run
3. Select your input files:
   - Sales Order file
   - Location mapping file
   - Lead Times file path
4. Click "Run Analysis"
5. View results in generated Excel file

### 📋 Input Files Required

**Sales Order File:**
- Tag No, Item Description, Qty, OA Date
- Cost Approval Remark, Account Remark, PPC Remark, Dispatch Remark

**Location File:**
- Item Categories/Group, Location

**Lead Times File:**
- Item Description, Lead Time, Item Categories/Group

### 💡 Tips
- Keep lead time file in same folder as .exe for easy reference
- Use absolute paths if files are in different directories
- Ensure date format is: DD MMM YYYY HH:MM:SS
```

### 3c. Attach the Executable

1. Scroll down to **Attachments** section
2. Drag and drop `SalesOrderAnalyzer.exe` 
3. Or click to browse and select the file

### 3d. Publish Release

Click **Publish release**

---

## 🔗 Share with Your Team

### Give them this link:
```
https://github.com/YOUR_USERNAME/SalesOrderAnalyzer/releases/download/v2.1/SalesOrderAnalyzer.exe
```

### Or:
```
https://github.com/YOUR_USERNAME/SalesOrderAnalyzer/releases
```

Users can download directly from the releases page!

---

## 📊 File Preparation Tips

### Sales Order File
- Ensure all timestamps are in format: `DD MMM YYYY HH:MM:SS`
- Example: `07 May 2026 14:30:45`
- All required columns must be present

### Location File
- Match Item Categories exactly with those in Lead Times file
- Use consistent naming (uppercase/lowercase matters)

### Lead Times File
- Can use multiple sheets: CONCEPT, MPPL, Lashing, Sheet1, Sheet2
- Lead Time can be: "5", "2 to 3 days", or "5 days"

---

## 🔄 Future Updates

When you make changes:

```bash
# On Mac, after making code changes:
git add .
git commit -m "Updated: Brief description of changes"
git push origin main

# Create new release tag:
git tag v2.2
git push origin v2.2

# GitHub Actions (if enabled) will automatically build new .exe
# Or manually build and create release v2.2 as shown in Step 3
```

---

## 🆘 Troubleshooting

### "Git command not found" on Mac
- Install Git: `brew install git`
- Or download from [git-scm.com](https://git-scm.com/download/mac)

### "Python not found" on Windows
- Download from [python.org](https://www.python.org/downloads)
- Check "Add Python to PATH" during installation

### Build fails on Windows
- Ensure Python 3.9+: `python --version`
- Update PyInstaller: `pip install --upgrade pyinstaller`
- Try manual build (not batch script)

### Executable won't run
- Try: Right-click → Run as Administrator
- Check antivirus isn't blocking it
- Ensure Windows 7 or later

### "File not found" during analysis
- Use absolute paths for files
- Ensure lead times file exists at specified location
- Check file permissions

---

## 📝 Repository Structure Final Checklist

```
✅ SalesOrderAnalyzer/
├── ✅ SO_analysis.py              (Main app with GUI)
├── ✅ SO_analysis.spec            (PyInstaller config)
├── ✅ requirements.txt            (Dependencies)
├── ✅ build.bat                   (Windows build script)
├── ✅ README.md                   (Full documentation)
├── ✅ QUICKSTART.md              (Quick reference)
├── ✅ GITHUB_SETUP.md            (This setup guide)
├── ✅ IMPLEMENTATION_SUMMARY.md  (What was done)
├── ✅ .gitignore                 (Git config)
├── ✅ .github/workflows/
│   └── ✅ build-windows.yml      (Automated builds)
└── 📁 dist/
    └── 📦 SalesOrderAnalyzer.exe (Generated .exe)
```

---

## ✨ You're All Set!

Your application is ready for:
- ✅ Version control on GitHub
- ✅ Distribution via GitHub Releases
- ✅ Easy updates and maintenance
- ✅ Team collaboration

**Happy coding! 🎉**

For any issues, refer to:
- README.md - Full documentation
- QUICKSTART.md - Quick reference
- GITHUB_SETUP.md - Setup details
