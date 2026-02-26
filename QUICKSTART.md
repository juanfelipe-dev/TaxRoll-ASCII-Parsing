# Quick Start Guide - Tax Roll Data Conversion

## 📋 Overview

This toolkit helps you convert fixed-width ASCII tax roll data into clean CSV format. It includes:
- **fixed_width_to_csv.py** - Main converter script
- **sftp_processor.py** - Optional SFTP download automation
- **examples.py** - Usage examples
- **schema.json** - Data field definitions
- **README.md** - Complete documentation

---

## 🚀 Getting Started in 5 Minutes

### Step 1: Prepare Your Files

1. **Get the data layout** from your SFTP provider
   - Also called "record layout" or "file specification"
   - Lists field names, positions, and lengths

2. **Obtain sample data** to test with
   - Download a small sample file from your SFTP server
   - Keep it in your working directory

### Step 2: Create Your Schema

The schema maps the fixed-width fields to CSV columns.

**Option A: Generate from Layout Document**

If you have this layout:
```
Position    Field              Length   Type
1-20        Parcel Number      20       Text
21-60       Owner Name         40       Text
61-75       Property Address   15       Text
76-85       Tax Amount         10       Numeric
```

Create `schema.json`:
```json
[
  {
    "name": "Parcel_Number",
    "start": 0,
    "length": 20,
    "type": "str"
  },
  {
    "name": "Owner_Name",
    "start": 20,
    "length": 40,
    "type": "str"
  },
  {
    "name": "Property_Address",
    "start": 60,
    "length": 15,
    "type": "str"
  },
  {
    "name": "Tax_Amount",
    "start": 75,
    "length": 10,
    "type": "float"
  }
]
```

**Note**: Subtract 1 from starting positions (layout docs use 1-based, Python uses 0-based)

**Option B: Use Sample Schema**

The included `sample_schema.json` shows the format - edit it for your fields.

### Step 3: Test the Conversion

```bash
# Convert your test file
python fixed_width_to_csv.py sample_input.txt output.csv --schema schema.json
```

**Expected output:**
```
INFO - Loaded schema from: schema.json
INFO - Parsing input file: sample_input.txt
INFO - Successfully parsed 1000 records
INFO - CSV successfully saved to: output.csv
```

### Step 4: Verify the Output

```bash
# Check the CSV file looks correct
head output.csv

# Count records
wc -l output.csv
```

### Step 5: Convert Your Full Dataset

Once the test passes:
```bash
python fixed_width_to_csv.py full_tax_roll.txt full_tax_roll.csv --schema schema.json
```

---

## 📊 Understanding the Schema

| Field | Meaning | Example |
|-------|---------|---------|
| **name** | CSV column header | "Owner_Name" |
| **start** | First character position (0-based) | 18 |
| **length** | Number of characters | 40 |
| **type** | Data type: str/int/float/date | "str" |
| **trim** | Remove whitespace? (default: true) | true |

### Common Type Conversions

- **str** - Text (default)
- **int** - Whole numbers (123, 456)
- **float** - Decimal numbers (1234.56)
- **date** - Date values (stored as text; parsed separately if needed)

---

## 🔄 Managing Weekly Updates

### Option 1: Manual Batch Scripts

**Windows batch file (`update_taxes.bat`):**
```batch
REM Weekly tax roll update
setlocal
cd C:\tax_data
python fixed_width_to_csv.py sftp_full_roll.txt full_roll_%date:~10,4%%date:~4,2%%date:~7,2%.csv --schema schema.json
python fixed_width_to_csv.py sftp_delin_roll.txt delin_roll_%date:~10,4%%date:~4,2%%date:~7,2%.csv --schema schema.json
```

Then schedule in **Task Scheduler** for weekly runs.

### Option 2: Using SFTP Processor

For automated downloads:

```bash
# First-time setup
python sftp_processor.py config
# Edit sftp_config.json with your credentials

# Then run weekly
python sftp_processor.py download
```

### Option 3: Python Script for Integration

```python
from fixed_width_to_csv import FixedWidthParser, save_to_csv, load_schema
from datetime import datetime

# Setup
schema = load_schema('schema.json')
parser = FixedWidthParser(schema)

# Get this week's file
today = datetime.now().strftime('%Y-%m-%d')

# Convert
records = parser.parse_file('sftp_full_roll.txt')
save_to_csv(records, f'full_roll_{today}.csv')
```

---

## ✅ Troubleshooting Checklist

### Problem: Fields misaligned or wrong data in CSV

**Checklist:**
1. ✓ Compare layout documentation with schema.json
2. ✓ Verify positions: Documentation might use 1-based, Python uses 0-based
   - Doc says "Position 1-20" = `"start": 0, "length": 20`
   - Doc says "Position 21-60" = `"start": 20, "length": 40`
3. ✓ Check field widths match exactly
4. ✓ Open input file in hex viewer or fixed-width editor to verify positions

### Problem: Missing or null values in output

**Troubleshooting:**
```bash
# Check input file structure
head -5 input.txt | cat -A    # Shows line endings and tabs

# View specific line with character positions
head -1 input.txt | cut -c1-80   # First 80 chars of first line
```

### Problem: Numeric fields showing as null

**Solution:** Field may contain non-numeric characters. Try:
1. Change type to "str" temporarily
2. Review raw data in those positions
3. Adjust schema as needed

### Problem: "FileNotFoundError" or encoding issues

```bash
# Check file exists and is readable
ls -l input.txt            # Linux/Mac
dir input.txt              # Windows

# Verify encoding (should work with UTF-8 and Latin-1)
# Script auto-handles most encodings
```

---

## 📁 File Organization

```
project/
├── fixed_width_to_csv.py    # Main converter
├── sftp_processor.py        # Optional SFTP automation
├── examples.py              # Usage examples
├── schema.json              # Your field definitions
├── input/
│   └── tax_roll.txt         # Input fixed-width file
└── output/
    └── tax_roll.csv         # Converted CSV
```

---

## 🎯 Common Use Cases

### Use Case 1: One-time Conversion

```bash
# Just convert existing file once
python fixed_width_to_csv.py tax_data.txt output.csv --schema schema.json
```

### Use Case 2: Weekly Updates

```bash
# Set up batch file to run automatically
# Then schedule it in Task Scheduler / cron
```

### Use Case 3: Data Quality Checks

See `examples.py` → **Example 4** for validation and cleanup patterns.

### Use Case 4: Filtering/Processing

See `examples.py` → **Example 2** for custom filtering patterns.

---

## 📞 Getting Help

### If the conversion fails:

Gather and share:
1. **Sample line** from your input file
2. **Official layout document** (field positions)
3. **Error message** from the script
4. **Your schema.json** file

### Common Questions:

**Q: Why are my numbers showing as text?**  
A: Schema field type is "str". Change to "int" or "float".

**Q: How do I handle dates?**  
A: Use `"type": "date"`. Check format matches your data.

**Q: Can it handle huge files?**  
A: Yes, up to millions of records. May need more RAM for very large files.

**Q: What's the character encoding?**  
A: Script auto-detects UTF-8 and Latin-1. Most tax data is ASCII-compatible.

---

## 🔗 Next Steps

1. **Get your actual layout** from the data provider
2. **Create your schema.json** based on field positions
3. **Test with sample data** from the SFTP server
4. **Convert full dataset** once test passes
5. **Automate weekly runs** using batch script or scheduler
6. **Review output CSV** to verify accuracy

---

## 📚 Full Documentation

See **[README.md](README.md)** for:
- Advanced features and options
- Custom processing examples
- Performance tuning
- Complete API reference

---

## Getting Started Right Now

```bash
# 1. Test with sample data
python fixed_width_to_csv.py sample.txt output.csv

# 2. Review the output
head output.csv

# 3. When ready, process full file
python fixed_width_to_csv.py full_data.txt full_output.csv

Done!
```

---

Good luck with your tax roll data conversion! 📊
