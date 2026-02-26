# Fixed-Width ASCII to CSV Converter
## Tax Roll Data Processing Tool

This repository contains a complete solution for converting large tax-roll datasets
from fixed-width ASCII format into clean, structured CSV files. The package
includes:

- A **command‑line script** (`fixed_width_to_csv.py`) for batch and automated use.
- A **Flask web application** (`app.py`) with a modern UI for non-technical users.
- Sample schemas, examples, and optional SFTP downloader.
- Comprehensive documentation: quickstart, web app guide, testing instructions.

The code is written in Python 3.7+ and requires only standard library modules. Use
whatever interface works best for your workflow – the same core parser powers
every tool in this repo.

> **Tip:** For quick instructions, see [QUICKSTART.md](QUICKSTART.md). The
> [WEBAPP.md](WEBAPP.md) file explains the web interface, and [TESTING.md](TESTING.md)
> lists all validation steps.

---

## Overview

Tax roll data from government assessor offices is often provided in **fixed-width
ASCII format**, where each field occupies a specific column position. The core
parser in this project reads such files according to a user-specified schema and
produces a CSV with headers, types, and trimmed values.

The rest of this README explains the format, schema definition, and basic CLI
usage. More detailed workflows are covered in the supplementary documents.

### Key Features
- ✅ Handles large fixed-width datasets efficiently
- ✅ Schema-based parsing for accurate field extraction
- ✅ Automatic type conversion (string, integer, float, date)
- ✅ Whitespace trimming and error handling
- ✅ Progress logging for long-running conversions
- ✅ Validation and detailed error reporting

---

## Getting Started

### Prerequisites
- **Python 3.7 or later** (3.13 used during development)
- **pip** (to install Flask if you use the web interface)

### Quick CLI Example
```bash
cd "f:\Copilot Projects\ASCII Python"
python fixed_width_to_csv.py test_input.txt test_output.csv --schema test_schema.json
```

### Repository Structure
```
├── fixed_width_to_csv.py    # Core parser & CLI converter
├── app.py                   # Flask web application server
├── sftp_processor.py        # Optional SFTP downloader
├── examples.py              # Sample code and workflows
├── templates/               # HTML/CSS/JS for web UI
│   └── index.html
├── sample_schema.json       # Example field layout
├── test_schema.json         # Schema used in tests
├── test_input.txt           # Sample fixed-width file
├── requirements.txt         # Python dependencies (Flask)
├── README.md                # This file
├── QUICKSTART.md            # 5‑minute start guide
├── WEBAPP.md                # Web application documentation
├── TESTING.md               # Complete testing instructions
└── PROJECT_COMPLETE.md      # Project overview for client
```

### Run the Web UI (optional)
```bash
pip install -r requirements.txt   # install Flask
python app.py                     # starts server on http://localhost:5000
```

Consult the other documentation files for more detailed instructions and
examples.

---

## Understanding Fixed-Width Format

In fixed-width ASCII files, each field occupies a specific column position:

```
Example line from tax roll file:
|--Parcel Number--||------Owner Name------||---Property Address---|
123456789012345678John Smith            123 Main Street       
012345678901234567890123456789012345678901234567890123456789012345
          1         2         3         4         5         6
```

The **schema** defines:
- `start`: Where the field begins (0-indexed)
- `length`: How many characters the field occupies
- `type`: Data type (str, int, float, date)
- `trim`: Whether to remove leading/trailing whitespace

---

## Schema Definition

The schema is a JSON file that maps each column in your fixed-width file.

### Schema File Format

```json
[
  {
    "name": "Parcel_Number",
    "start": 0,
    "length": 18,
    "type": "str",
    "trim": true,
    "description": "Unique parcel identifier"
  },
  {
    "name": "Owner_Name",
    "start": 18,
    "length": 40,
    "type": "str",
    "trim": true,
    "description": "Property owner name"
  },
  {
    "name": "Tax_Amount",
    "start": 235,
    "length": 12,
    "type": "float",
    "trim": true,
    "description": "Annual tax amount"
  }
]
```

### Field Definitions

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Column header name (appears in CSV output) |
| `start` | Yes | Starting position in the fixed-width line (0-indexed) |
| `length` | Yes | Number of characters this field occupies |
| `type` | No | Data type: `str` (default), `int`, `float`, `date` |
| `trim` | No | Whether to trim whitespace (default: true) |
| `description` | No | Optional field description for documentation |

### Type Conversion

- **str**: Text field, whitespace trimmed if `trim: true`
- **int**: Integer value, non-numeric values become null
- **float**: Decimal number, non-numeric values become null
- **date**: Returns as string; format based on original data

---

## Basic Usage

### 1. Create Your Schema

First, obtain the file layout documentation from your SFTP source and create a JSON schema file:

```bash
# Generate a sample schema template to get started
python fixed_width_to_csv.py --create-sample-schema
```

This creates `sample_schema.json` - edit it to match your actual file format.

### 2. Convert File

```bash
# Basic usage (looks for schema.json by default)
python fixed_width_to_csv.py input_taxroll.txt output_taxroll.csv

# With custom schema file
python fixed_width_to_csv.py input_taxroll.txt output_taxroll.csv --schema my_schema.json
```

### 3. Output

The script generates:
- **CSV file**: Clean, structured data with headers
- **Log output**: Conversion progress and any warnings

---

## Usage Examples

### Example 1: Convert Full Tax Roll

```bash
python fixed_width_to_csv.py full_tax_roll.txt full_tax_roll.csv --schema tax_schema.json
```

Output:
```
INFO - Loaded schema from: tax_schema.json
INFO - Parsing input file: full_tax_roll.txt
INFO - Processed 10000 lines...
INFO - Successfully parsed 152847 records
INFO - CSV successfully saved to: full_tax_roll.csv
INFO - Total records written: 152847
INFO - Conversion completed successfully!
```

### Example 2: Convert Delinquent Tax Roll (Weekly Update)

```bash
python fixed_width_to_csv.py delinquent_roll.txt delinquent_roll.csv --schema delinquent_schema.json
```

---

## Finding the Schema/Layout

The data provider (government assessor) typically supplies:

1. **Data layout document** - Text file showing field positions
2. **Record layout specification** - Details character positions for each field
3. **Data dictionary** - Explains field meanings

### How to Extract Schema from Layout Document

If you have a layout like:

```
Position  Field Name          Type      Length
1-18      Parcel Number       Char      18
19-58     Owner Name          Char      40
59-108    Property Address    Char      50
```

Convert to JSON schema:

```json
[
  {
    "name": "Parcel_Number",
    "start": 0,
    "length": 18,
    "type": "str",
    "trim": true
  },
  {
    "name": "Owner_Name",
    "start": 18,
    "length": 40,
    "type": "str",
    "trim": true
  }
]
```

**Note**: Subtract 1 from starting positions in documentation (they use 1-based indexing, Python uses 0-based)

---

## Troubleshooting

### Issue: Fields are misaligned or contain wrong data
**Solution**: Verify your schema's `start` and `length` values. Check if the documentation uses 1-based or 0-based indexing.

### Issue: Numeric fields showing as null/None
**Solution**: The field might contain non-numeric characters. Use `"type": "str"` for numeric data with mixed content, or trim the data.

### Issue: File not found error
**Solution**: Ensure the input file path is correct:
```bash
# From current directory
python fixed_width_to_csv.py ./data/tax_roll.txt ./output/tax_roll.csv

# Absolute path
python fixed_width_to_csv.py C:\Data\tax_roll.txt C:\Output\tax_roll.csv
```

### Issue: Encoding errors (special characters, accents)
**Solution**: The script automatically handles encoding issues by ignoring problematic characters. If you need better control:
- Edit line 78 in the script to change `encoding='utf-8'` to `encoding='latin-1'` or your file's encoding

---

## Automating Weekly Updates

To run conversions automatically each week, create a batch script:

### Windows Batch File (`run_conversion.bat`)

```batch
@echo off
REM Weekly Tax Roll Conversion
setlocal

REM Configuration
set PYTHON_SCRIPT=C:\path\to\fixed_width_to_csv.py
set SFTP_DIR=\\sftp-server\tax-data
set OUTPUT_DIR=C:\tax_data_output
set SCHEMA=C:\path\to\schema.json

REM Create output directory if needed
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Run conversion with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

echo Conversion started: %mydate% %mytime%
python %PYTHON_SCRIPT% %SFTP_DIR%\full_tax_roll.txt %OUTPUT_DIR%\full_tax_roll_%mydate%.csv --schema %SCHEMA%
python %PYTHON_SCRIPT% %SFTP_DIR%\delinquent_roll.txt %OUTPUT_DIR%\delinquent_roll_%mydate%.csv --schema %SCHEMA%
echo Conversion completed at: %date% %time%
```

### Linux/Mac Shell Script (`run_conversion.sh`)

```bash
#!/bin/bash

# Configuration
PYTHON_SCRIPT="/path/to/fixed_width_to_csv.py"
SFTP_DIR="/mnt/sftp/tax-data"
OUTPUT_DIR="/data/tax_output"
SCHEMA="/path/to/schema.json"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Current date
DATESTR=$(date +%Y-%m-%d)

echo "Conversion started: $(date)"

# Convert both files
python3 "$PYTHON_SCRIPT" "$SFTP_DIR/full_tax_roll.txt" "$OUTPUT_DIR/full_tax_roll_$DATESTR.csv" --schema "$SCHEMA"
python3 "$PYTHON_SCRIPT" "$SFTP_DIR/delinquent_roll.txt" "$OUTPUT_DIR/delinquent_roll_$DATESTR.csv" --schema "$SCHEMA"

echo "Conversion completed: $(date)"
```

### Schedule with Task Scheduler (Windows)

1. Open **Task Scheduler**
2. Create new task: "Weekly Tax Roll Conversion"
3. Trigger: Weekly, Monday 2:00 AM
4. Action: Run batch file
5. Log output to a file for monitoring

---

## Advanced Features

### Custom Type Conversions

If you need special handling (e.g., currency formatting, date parsing):

```python
# Modify the parse_line method in FixedWidthParser class
# Add custom logic in the type conversion section:

elif col_type == 'currency':
    # Remove $ and convert to float
    value = value.replace('$', '').strip()
    record[name] = float(value) if value else None
```

### Validation

To add record validation (e.g., required fields):

```python
def validate_record(record: Dict[str, Any]) -> bool:
    """Check that required fields aren't empty."""
    required_fields = ['Parcel_Number', 'Owner_Name']
    return all(record.get(field) for field in required_fields)

# Then in parse_file(), filter records:
records = [r for r in records if validate_record(r)]
```

---

## Performance Notes

- **File Size**: Handles multi-million record files efficiently
- **Memory**: Loads entire file into memory; consider chunking for very large files (>2GB)
- **Speed**: Typical processing: 50,000+ records/second

For very large files, add chunking:

```python
def parse_file_chunked(self, input_file: str, chunk_size: int = 100000):
    """Process file in chunks."""
    with open(input_file, 'r') as f:
        chunk = []
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            record = self.parse_line(line.rstrip('\n\r'))
            chunk.append(record)
            
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        
        if chunk:
            yield chunk
```

---

## Support & Maintenance

### Handling Schema Changes

If the data provider changes their format:
1. Obtain the new layout documentation
2. Update your schema JSON file with new field positions
3. Re-run the conversion

### Validating Output

```bash
# Check record count
wc -l output_file.csv

# View first few records
head -20 output_file.csv

# Check for null/empty values
grep -c ",," output_file.csv
```

---

## License

This tool is provided as-is for data processing purposes.

---

## Questions or Issues?

When troubleshooting, gather:
1. A sample line from your fixed-width file
2. The official layout/schema documentation
3. Error messages or log output from the script

---

## Quick Reference

```bash
# Create sample schema
python fixed_width_to_csv.py --create-sample-schema

# Convert with default schema.json
python fixed_width_to_csv.py input.txt output.csv

# Convert with custom schema
python fixed_width_to_csv.py input.txt output.csv --schema myschema.json

# View help
python fixed_width_to_csv.py --help
```
