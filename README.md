# Sales Order Analyzer v2.1

A comprehensive analysis tool for sales order data with advanced timestamp parsing, lead time calculation, and bottleneck identification.

## Features

- **GUI Interface**: User-friendly desktop application for easy file selection and analysis
- **Lead Time Calculation**: MSQ-based lead time calculation with fuzzy matching
- **Bottleneck Analysis**: Identifies delays and bottlenecks in the order processing pipeline
- **Item Location Mapping**: Maps items to warehouse locations by category
- **Timestamp Analysis**: Extracts and analyzes all timestamps across multiple remark fields
- **Excel Export**: Generates detailed analysis reports in Excel format

## Installation & Building (Windows)

### Option 1: Using Portable Python (Recommended - No Installation Required)

1. **Download Portable Python**:
   - Visit [WinPython](https://github.com/winpython/winpython/releases)
   - Download the latest portable version (e.g., `WinPython-64bit-3.9.x.exe` or `.zip`)
   - Extract to a folder (e.g., `C:\PortablePython`)

2. **Install Dependencies**:
   ```
   cd C:\PortablePython
   Scripts\pip.exe install -r requirements.txt
   ```

3. **Build the .exe**:
   ```
   Scripts\python.exe -m PyInstaller SO_analysis.spec
   ```

4. **Find Your Executable**:
   - The `SalesOrderAnalyzer.exe` will be in the `dist` folder

### Option 2: Using Standard Python Installation

1. **Install Python**:
   - Download from [python.org](https://www.python.org/downloads/)
   - Choose Python 3.9 or later
   - During installation, check "Add Python to PATH"

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Build the .exe**:
   ```
   pyinstaller SO_analysis.spec
   ```

## Running the Application

### From Source:
```
python SO_analysis.py
```

### From Built Executable:
- Simply run `SalesOrderAnalyzer.exe` from the `dist` folder
- No Python or dependencies needed!

## Using the Application

1. **Sales Order File** (Required):
   - Select your sales order Excel file
   - Should contain columns: Tag No, Item Description, Qty, OA Date, Cost Approval Remark, Account Remark, PPC Remark, Dispatch Remark

2. **Location File** (Required):
   - Select your location mapping file
   - Should contain columns: Item Categories (or Item Group), Location

3. **Lead Times File Path** (Default: `Lead Time file.xlsx`):
   - Specify the path to lead times reference file
   - By default, it looks for `Lead Time file.xlsx` in the same directory as the .exe
   - Can be an absolute path (e.g., `C:\Data\Lead Time file.xlsx`)

4. **Output File Location**:
   - Choose where to save the analysis results
   - Default: `Analysis_Output.xlsx` in the current directory

5. **Click "Run Analysis"**:
   - The tool will process the data and generate the report
   - You'll see a success message when complete

## File Requirements

### Sales Order File
Required columns:
- `Tag No`: Item tag/reference number
- `Item Description`: Description of the item
- `Qty`: Order quantity
- `OA Date`: Order approval date (format: DD MMM YYYY HH:MM:SS)
- `Cost Approval Remark`: Timestamp and remarks (format: DD MMM YYYY HH:MM:SS ...)
- `Account Remark`: Timestamp and remarks (format: DD MMM YYYY HH:MM:SS ...)
- `PPC Remark`: Timestamp and remarks (format: DD MMM YYYY HH:MM:SS ...)
- `Dispatch Remark`: Timestamp and remarks (format: DD MMM YYYY HH:MM:SS ...)

### Lead Times File
Required columns:
- `Item Description`: Item name to match orders
- `Lead Time`: Lead time in days (e.g., "5", "2 to 3", "5 days")
- `Item Categories` or `Item Group` or `Item Category`: Item classification
- Optional: `Confirmed MSQ if any`, `Batch production quantity per day`

### Location File
Required columns:
- `Item Categories` or `Item Group` or `Item Category`: Item classification
- `Location`: Storage location or warehouse name

## Output

The analysis generates a comprehensive Excel file with:
- All original order data
- Parsed timestamps from all remarks
- Lead time calculations
- Item categories and locations
- Time differences between each processing stage
- Bottleneck analysis
- Scheduled dispatch information

## Troubleshooting

**"File not found" error**:
- Ensure all file paths are correct and accessible
- Use absolute paths if files are in different directories

**"No module named X" error when running from source**:
- Run: `pip install -r requirements.txt`

**Excel file won't open**:
- Ensure you have write permissions to the output directory
- Try a different filename

## Version Information

- **Version**: 2.1
- **Python**: 3.9+
- **Platform**: Windows, macOS, Linux
- **Executable Platform**: Windows only (when built with .spec)

## Support

For issues or questions:
1. Check that all input files are in Excel format (.xlsx or .xls)
2. Verify column names match the requirements
3. Ensure date formats are correct (DD MMM YYYY HH:MM:SS)

## License

This tool is provided as-is for internal analysis purposes.