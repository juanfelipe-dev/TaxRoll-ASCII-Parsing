# Tax Roll Converter - Complete Testing Guide

## 🧪 Test Overview

This guide covers testing the complete tax roll converter project, including:
- Command-line interface (CLI)
- Web application interface
- SFTP automation (optional)
- Real-world scenarios

---

## Part 1: CLI Testing

### Test 1.1: Basic Conversion

**Setup:**
```bash
cd "f:\Copilot Projects\ASCII Python"
```

**Create test file:**
```powershell
# create_test_data.ps1
$lines = @()
$lines += "123456789012345678901St" + "John Smith".PadRight(40) + "123 Main St".PadRight(35)
$lines | Out-File test_basic.txt

# View the file
Get-Content test_basic.txt -Encoding UTF8
```

**Run conversion:**
```bash
python fixed_width_to_csv.py test_input.txt test_output.csv --schema test_schema.json
```

**Expected Output:**
```
2026-02-25 17:04:10,195 - INFO - Loaded schema from: test_schema.json
2026-02-25 17:04:10,195 - INFO - Parsing input file: test_input.txt
2026-02-25 17:04:10,195 - INFO - Successfully parsed 5 records
2026-02-25 17:04:10,195 - INFO - CSV successfully saved to: test_output.csv
```

**Verify output:**
```bash
# Check CSV was created
Get-Content test_output.csv -TotalCount 5

# Count records
(Get-Content test_output.csv | Measure-Object -Line).Lines
```

### Test 1.2: Schema Validation

**Test with invalid schema:**
```bash
# Create bad schema (overlapping fields)
python -c "
import json
bad_schema = [
    {'name': 'Field1', 'start': 0, 'length': 20},
    {'name': 'Field2', 'start': 10, 'length': 20}  # Overlaps!
]
with open('bad_schema.json', 'w') as f:
    json.dump(bad_schema, f)
"

python fixed_width_to_csv.py test_input.txt output_bad.csv --schema bad_schema.json
```

**Expected:** Logs warning about field overlap.

### Test 1.3: Type Conversion

**Create test with mixed types:**
```python
# Create test with numeric fields
schema = [
    {"name": "ID", "start": 0, "length": 10, "type": "int"},
    {"name": "Name", "start": 10, "length": 20, "type": "str"},
    {"name": "Amount", "start": 30, "length": 12, "type": "float"}
]
```

**Verify CSV contains correct types:**
```bash
head test_output.csv
# ID should be numeric, Amount should have decimals
```

---

## Part 2: Web Application Testing

### Test 2.1: Access Web Interface

**Start the server:**
```bash
# If not already running
python app.py
```

**Access in browser:**
```
http://localhost:5000
```

**Expected:**
- Modern, responsive interface loads
- Two-column layout (left: converter, right: help)
- All buttons and tabs visible

### Test 2.2: Schema Management

**Test Sample Templates:**
1. Click "Load Full Roll Template"
   - Should populate 11 fields
   - Verify field positions make sense
   - Status shows "✓ Schema Valid"

2. Click "Load Delinquent Template"
   - Should populate 8 fields for delinquent data
   - Fields include: Current_Tax_Due, Prior_Years_Due, etc.

**Test Manual Schema Edit:**
1. Click "+ Add Field"
   - New field appears at bottom
2. Enter values:
   - Name: "TestField"
   - Start: "50"
   - Length: "25"
   - Type: "str"
3. Status badge shows "✓ Schema Valid"

**Test Field Removal:**
1. Click ✕ next to a field
   - Field removes from list
   - Schema revalidates

### Test 2.3: File Upload & Preview

**Upload test file:**
1. Click "Select Fixed-Width File"
2. Choose `test_input.txt`
3. Preview appears showing:
   - First 10 lines of file
   - Line count
   - Chars per line

**Verify alignment:**
1. Review preview vs schema
2. Check if field widths match actual data

### Test 2.4: File Conversion

**Complete workflow:**
1. Upload file: `test_input.txt`
2. Load schema: "Load Full Roll Template"
3. Click "🚀 Convert to CSV"
4. Wait for processing
5. Verify:
   - Status shows "✓ Conversion Successful"
   - Record count displays: "5 records converted"
   - Download button appears

**Download output:**
1. Click "⬇️ Download CSV"
2. File automatically downloads
3. Verify:
   - CSV contains headers
   - Data properly formatted
   - No truncation or corruption

### Test 2.5: Schema Paste/Import

**Test JSON paste:**
1. Go to "Paste JSON" tab
2. Paste valid schema:
   ```json
   [{"name":"Field1","start":0,"length":20,"type":"str"}]
   ```
3. Click "Load from Paste"
4. Verify schema loads in editor

### Test 2.6: Layout Extraction

**Test auto-extraction:**
1. Go to "From Layout" tab
2. Paste layout documentation:
   ```
   1-20 Parcel Number
   21-60 Owner Name
   61-90 Property Address
   ```
3. Click "Extract Schema"
4. Verify:
   - 3 fields created
   - Positions correct (0-19, 20-59, 60-89)
   - Names converted to underscores

---

## Part 3: Error Handling Tests

### Test 3.1: Invalid File Upload

**Test missing file:**
1. Click "Convert to CSV" without selecting file
2. **Expected:** Error message "Please select a file"

**Test unsupported format:**
1. Upload a .docx or .exe file
2. **Expected:** Error about file type

### Test 3.2: Schema Errors

**Test empty schema:**
1. Clear all fields (remove all rows)
2. Click "Convert to CSV"
3. **Expected:** Error "Please define at least one field"

**Test invalid JSON paste:**
1. Go to "Paste JSON" tab
2. Paste invalid JSON: `{"bad": json}`
3. Click "Load from Paste"
4. **Expected:** "Invalid JSON" error message

### Test 3.3: Malformed Data

**Test file too short:**
1. Create file shorter than schema expects
2. Attempt conversion
3. **Expected:** Graceful handling, partial field extraction

---

## Part 4: Performance Tests

### Test 4.1: Large File Processing

**Create large test file:**
```python
# Generate 10,000 test records
with open('large_test.txt', 'w') as f:
    for i in range(10000):
        line = f"{str(i).zfill(20)}"
        line += f"Owner {i}".ljust(40)
        line += "Address Line".ljust(35)
        f.write(line + '\n')
```

**Convert:**
1. Upload `large_test.txt`
2. Use existing schema
3. Click "Convert to CSV"
4. **Expected:**
   - Completes in < 5 seconds
   - 10,000 records converted
   - CSV file generated

### Test 4.2: Complex Schema

**Test with many fields:**
1. Create schema with 50+ fields
2. Upload matching file
3. Verify conversion completes

---

## Part 5: Integration Tests

### Test 5.1: End-to-End CLI

**Complete workflow:**
```bash
# 1. Create sample data
# (provided in test_input.txt)

# 2. Create schema
# (use test_schema.json)

# 3. Convert
python fixed_width_to_csv.py test_input.txt final_output.csv --schema test_schema.json

# 4. Verify result
Get-Content final_output.csv | Select-Object -First 3
```

### Test 5.2: End-to-End Web

**Complete workflow:**
1. Open http://localhost:5000
2. Click "Load Full Roll Template"
3. Upload test_input.txt
4. Click "Convert to CSV"
5. Download CSV
6. Open file in Excel/spreadsheet to verify

### Test 5.3: Cross-Platform

**Test on different systems:**
- Windows (PowerShell): ✓ CMD works
- Linux/Mac (Bash): ✓ Shell scripts work
- Web: ✓ Cross-browser compatible

---

## Part 6: Real-World Scenario Tests

### Scenario A: Weekly Batch Update

**Simulate weekly process:**
1. Prepare fresh file: `tax_roll_2024-02-25.txt`
2. Load saved schema from JSON
3. Convert to CSV
4. Name output with date: `tax_roll_2024-02-25.csv`
5. Verify records, metadata, no errors

### Scenario B: Schema Discovery

**New data format testing:**
1. Receive new file spec from provider
2. Go to "From Layout" tab
3. Paste layout specification
4. Auto-extract schema
5. Adjust if needed
6. Test conversion

### Scenario C: Data Quality Validation

**Verify output quality:**
1. Convert sample file
2. Open CSV in spreadsheet
3. Check:
   - Headers are correct
   - Data types align
   - No null/empty unexpected values
   - Thousands of records match

---

## Part 7: Browser Compatibility

### Test on Different Browsers

- **Chrome/Edge**: ✓ Full support
- **Firefox**: ✓ Full support
- **Safari**: ✓ Check file upload
- **Mobile Browser**: ✓ Responsive design
- **IE 11**: Will not work (uses modern JS)

### Test Responsive Design

1. Open on mobile device or use responsive mode
2. Verify:
   - Single column layout
   - Buttons are touch-friendly
   - File preview scrollable
   - All tabs accessible

---

## Part 8: Documentation Tests

### Test 1: README Accuracy
- Follow all steps in README.md
- Verify they work as documented
- Check examples run correctly

### Test 2: QUICKSTART Accuracy
- Follow 5-minute quick start
- Verify task completion
- Check all links work

### Test 3: WEBAPP Guide
- Follow web app instructions
- Test all referenced features
- Verify screen layouts match

---

## Test Checklist

```
□ CLI basic conversion works
□ Web interface loads
□ File upload successful
□ Schema validation works
□ Conversion completes
□ CSV downloads correctly
□ Large files handled
□ Error messages display
□ Sample templates load
□ Layout extraction works
□ Type conversion correct
□ Multiple browsers work
□ Responsive design works
□ Documentation accurate
□ Performance acceptable
```

---

## Troubleshooting During Testing

### Flask won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process or change port in app.py
```

### File upload fails
```bash
# Check file permissions
# Check temp directory accessible
# Verify disk space available
```

### Schema parsing errors
```bash
# Verify JSON is valid
# Check field positions don't overlap
# Ensure lengths match file structure
```

### Conversion is slow
```bash
# Check CPU/RAM available
# Try smaller file first
# Check for disk I/O bottlenecks
```

---

## Success Criteria

All tests pass when:
- ✅ CLI converts files accurately
- ✅ Web UI is responsive and intuitive
- ✅ Schema validation prevents errors
- ✅ Large files handled efficiently
- ✅ Error messages are helpful
- ✅ Output CSV is correct
- ✅ Documentation is accurate
- ✅ Multiple browsers supported
- ✅ Performance is acceptable

---

## Test Execution Schedule

**Quick Tests** (5 min):
- Basic CLI conversion
- Web UI loads
- Sample template loads
- File upload/convert

**Full Tests** (30 min):
- All CLI features
- All web features
- Error handling
- Performance

**Regression Tests** (Before release):
- All above
- Browser compatibility
- Large file testing
- Documentation review

---

## Results Reporting

After running tests, report:
1. **What was tested** - Which parts of the project
2. **Results** - Passed/Failed for each test
3. **Issues found** - Any problems discovered
4. **Performance metrics** - Speed, size limits
5. **Browser compatibility** - Tested browsers
6. **Recommendations** - Suggested improvements

---

**Ready to test? Start with "Test 2.1: Access Web Interface"!** 🚀
