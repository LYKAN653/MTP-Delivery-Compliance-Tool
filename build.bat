@echo off
REM Build script for Windows to create SalesOrderAnalyzer.exe
REM This script assumes Python and dependencies are already installed

echo.
echo ========================================
echo Sales Order Analyzer - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo [1/4] Python found. Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [2/4] Installing PyInstaller...
    python -m pip install pyinstaller
) else (
    echo [2/4] PyInstaller already installed
)

echo [3/4] Building executable...
echo Please wait, this may take a few minutes...
echo.

REM Build using the spec file
python -m pyinstaller SO_analysis.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Your executable is located at:
echo   dist\SalesOrderAnalyzer.exe
echo.
echo To run the application:
echo   1. Navigate to the dist folder
echo   2. Double-click SalesOrderAnalyzer.exe
echo.
pause
