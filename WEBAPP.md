# Tax Roll Converter Web App

A modern, user-friendly web interface for converting fixed-width ASCII tax roll data to CSV format.

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the app:**
```bash
python app.py
```

3. **Open in browser:**
```
http://localhost:5000
```

The app will be available at http://localhost:5000

---

## 📋 Features

### ✅ File Upload
- Drag-and-drop or click to select files
- Supports: .txt, .dat, .asc, .csv
- Max file size: 500MB
- Automatic line preview (first 10 lines)

### ✅ Schema Management
Three ways to define your schema:

1. **Visual Editor** - Build schema field by field
2. **JSON Paste** - Paste pre-made JSON schemas
3. **Layout Extraction** - Extract from file layout documentation

### ✅ Smart Features
- Real-time schema validation
- Field position overlap detection
- Live file preview
- Sample schema templates
- Record count reporting

### ✅ Download
- Automatic CSV generation
- Timestamped file naming
- Direct download to your computer

---

## 🎯 How to Use

### Step 1: Define Your Schema

**Option A: Use Sample Template**
1. Click "Load Full Roll Template" or "Load Delinquent Template"
2. Templates auto-populate with common tax roll fields
3. Modify as needed

**Option B: Extract From Layout**
1. Go to "From Layout" tab
2. Paste your file specification:
   ```
   1-20 Parcel Number
   21-60 Owner Name
   61-75 Property Address
   ```
3. Click "Extract Schema"

**Option C: Manual Editor**
1. Go to "Editor" tab
2. Click "+ Add Field" for each column
3. Enter:
   - **Name**: CSV column header
   - **Start**: Character position (0-based)
   - **Length**: Number of characters
   - **Type**: str/int/float/date

### Step 2: Upload File

1. Click "Select Fixed-Width File"
2. Choose your data file
3. Review the preview to verify alignment

### Step 3: Convert

1. Click "🚀 Convert to CSV"
2. Wait for conversion to complete
3. Click "⬇️ Download CSV" to save the file

---

## 💡 Schema Definition Guide

### Understanding Field Positions

Your file layout might look like:
```
Position    Field           Length
1-20        Parcel Number   20
21-60       Owner Name      40
61-90       Address         30
```

Convert to schema (subtract 1 for start position):
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
    "name": "Address",
    "start": 60,
    "length": 30,
    "type": "str"
  }
]
```

### Field Types

| Type | Usage | Example |
|------|-------|---------|
| **str** | Text data | "John Smith", "123 Main St" |
| **int** | Whole numbers | 1250000, 15000 |
| **float** | Decimals | 12500.50, 3.14 |
| **date** | Dates | 2024-01-15 |

---

## 🔍 File Preview Tips

After uploading, the preview shows the first 10 lines with:
- **Line count**: How many preview lines
- **Line length**: Total characters per line (should equal sum of schema field lengths)

Example:
```
12345678901234567890John Smith    123 Main Street    2024
```

If line length = 195 characters, all schema fields should sum to 195.

---

## 🧪 Test Workflow

### Create Test Data

1. Create `test_data.txt` with fixed-width records
2. Verify line lengths match your schema

Example schema:
```json
[
  {"name": "ID", "start": 0, "length": 10, "type": "str"},
  {"name": "Name", "start": 10, "length": 30, "type": "str"},
  {"name": "Amount", "start": 40, "length": 10, "type": "float"}
]
```

Example data (matches positions):
```
1234567890John Smith         1234567890         12500.00
9876543210Jane Doe           1234567890         25000.00
```

### Upload & Convert

1. Go to http://localhost:5000
2. Upload test_data.txt
3. Enter schema (or use template)
4. Click "Convert to CSV"
5. Verify output CSV contains correct data

---

## 📊 Sample Templates

### Full Tax Roll
Includes:
- Parcel Number
- Owner Name
- Property Address
- Land Use Code
- Assessed Value
- Tax Amount
- Tax Year

### Delinquent Roll
Includes:
- Parcel Number
- Owner Name
- Current Tax Due
- Prior Years Due
- Penalties & Interest
- Total Delinquent
- Last Payment Date

---

## 🛠️ Advanced Features

### Save Schema as JSON

In "Paste JSON" tab:
1. Edit your schema
2. Copy the JSON from "Editor" tab
3. Save to file
4. Reload later by pasting

### Batch Conversion

Note: Web app processes one file at a time. For automation use CLI:
```bash
python fixed_width_to_csv.py input1.txt output1.csv --schema schema.json
python fixed_width_to_csv.py input2.txt output2.csv --schema schema.json
```

### Schedule Weekly Updates

Create batch script (`update.bat`):
```batch
python app.py
REM Browser will open at http://localhost:5000
REM Manual upload and conversion
```

Or use CLI for full automation (see [README.md](README.md)).

---

## 🐛 Troubleshooting

### Issue: Fields are misaligned

**Solution:**
1. Check file preview - visually verify field boundaries
2. Count characters: Document says "Position 1-20" = Start: 0, Length: 20
3. Verify sum of lengths = total line width shown in preview

### Issue: Fields contain wrong data

**Solution:**
1. Make sure **Start** positions are correct
2. Make sure **Length** matches field width exactly
3. Beware: Some docs use 1-based, this tool uses 0-based positions

### Issue: Numbers aren't converting

**Solution:**
1. Check field type is set correctly (int or float)
2. If field contains mixed characters, use "str" type
3. Leading zeros should be fine (auto-trimmed)

### Issue: File upload fails

**Solution:**
1. Check file size < 500MB
2. Use supported format: .txt, .dat, .asc, or .csv
3. Try a smaller sample file first

### Issue: Conversion is slow

**Solution:**
- Normal for large files (millions of records)
- Processing roughly 50,000 records/second
- Check JavaScript console for any client-side errors

---

## 🌐 Running on Different Machines

### Change Access Port

Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### Access from Network

Replace `localhost` with your IP address:
```
http://192.168.1.100:5000
```

Note: Requires network access to be configured.

---

## 📈 API Reference

The web app has several API endpoints for programmatic use:

### Get Default Schema
```
GET /api/schema/default
```
Returns a basic schema template.

### Get Sample Schemas
```
GET /api/schema/sample/<type>
```
Types: `full_roll`, `delinquent`

### Convert File
```
POST /api/convert
- file: (multipart file upload)
- schema: (JSON string)
```

### Validate Schema
```
POST /api/validate_schema
- schema: (JSON string or object)
```

### Preview File
```
POST /api/preview
- file: (multipart file upload)
```

### Extract Schema from Layout
```
POST /api/extract_schema
- layout_text: (text specification)
```

### Download Results
```
GET /api/download/<filename>
```

---

## 💾 Database & Storage

- **Upload folder**: System temp directory
- **Output files**: Timestamped for tracking
- **Auto-cleanup**: Files are temporary and may be cleaned by OS

For production, modify `app.py` to use persistent storage:
```python
app.config['UPLOAD_FOLDER'] = '/path/to/persistent/storage'
```

---

## 📞 Support

### Common Questions

**Q: Can I upload multiple files at once?**  
A: Not in web UI. Use CLI with batch scripts for automation.

**Q: Are my files stored on the server?**  
A: Files are temporarily stored then can be deleted. For sensitive data, use local CLI version.

**Q: Can I share schemas with others?**  
A: Yes! Export as JSON and import via "Paste JSON" tab.

**Q: What's the maximum file size?**  
A: 500MB limit. Modify in app.py to increase.

---

## 🔒 Security Notes

- File uploads stored in system temp directory
- No files are sent to external servers
- All processing is local
- No authentication (add Flask-Login for production)

---

## 🚀 Next Steps

1. **Test with sample data** - Use provided templates
2. **Get your layout docs** - Contact data provider
3. **Create your schema** - Use extraction tool
4. **Process full dataset** - Upload and convert
5. **Automate weekly** - Set up cron job or scheduler

---

## 📚 Related Files

- [README.md](README.md) - Full CLI documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [fixed_width_to_csv.py](fixed_width_to_csv.py) - Core converter logic
- [examples.py](examples.py) - Usage examples

---

**Ready to convert? Open http://localhost:5000 and start processing your tax roll data!** 📊
