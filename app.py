"""
Tax Roll Converter Web Application
==================================

Flask web app for converting fixed-width ASCII files to CSV.
"""

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import json
import tempfile
from datetime import datetime
import logging

from fixed_width_to_csv import FixedWidthParser, save_to_csv, load_schema

# Configure Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'csv', 'dat', 'asc'}


def allowed_file(filename):
    """Check if uploaded file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/schema/default', methods=['GET'])
def get_default_schema():
    """Get default schema template."""
    schema = [
        {
            "name": "Parcel_Number",
            "start": 0,
            "length": 18,
            "type": "str",
            "trim": True,
            "description": "Unique parcel identifier"
        },
        {
            "name": "Owner_Name",
            "start": 18,
            "length": 40,
            "type": "str",
            "trim": True,
            "description": "Property owner name"
        },
        {
            "name": "Tax_Amount",
            "start": 235,
            "length": 12,
            "type": "float",
            "trim": True,
            "description": "Annual tax amount"
        }
    ]
    return jsonify(schema)


@app.route('/api/schema/sample/<schema_type>', methods=['GET'])
def get_sample_schema(schema_type):
    """Get sample schemas for different types."""
    schemas = {
        'full_roll': [
            {"name": "Parcel_Number", "start": 0, "length": 18, "type": "str", "trim": True},
            {"name": "Owner_Name", "start": 18, "length": 40, "type": "str", "trim": True},
            {"name": "Owner_Address", "start": 58, "length": 50, "type": "str", "trim": True},
            {"name": "Property_Address", "start": 108, "length": 50, "type": "str", "trim": True},
            {"name": "City", "start": 158, "length": 20, "type": "str", "trim": True},
            {"name": "State", "start": 178, "length": 2, "type": "str", "trim": True},
            {"name": "Zip_Code", "start": 180, "length": 10, "type": "str", "trim": True},
            {"name": "Land_Use_Code", "start": 190, "length": 3, "type": "str", "trim": True},
            {"name": "Total_Assessed_Value", "start": 193, "length": 12, "type": "int", "trim": True},
            {"name": "Tax_Amount", "start": 205, "length": 12, "type": "float", "trim": True},
            {"name": "Tax_Year", "start": 217, "length": 4, "type": "int", "trim": True},
        ],
        'delinquent': [
            {"name": "Parcel_Number", "start": 0, "length": 18, "type": "str", "trim": True},
            {"name": "Owner_Name", "start": 18, "length": 40, "type": "str", "trim": True},
            {"name": "Property_Address", "start": 58, "length": 50, "type": "str", "trim": True},
            {"name": "Current_Tax_Due", "start": 108, "length": 12, "type": "float", "trim": True},
            {"name": "Prior_Years_Due", "start": 120, "length": 12, "type": "float", "trim": True},
            {"name": "Penalties_Interest", "start": 132, "length": 12, "type": "float", "trim": True},
            {"name": "Total_Delinquent", "start": 144, "length": 12, "type": "float", "trim": True},
            {"name": "Last_Payment_Date", "start": 156, "length": 10, "type": "str", "trim": True},
        ]
    }
    return jsonify(schemas.get(schema_type, []))


@app.route('/api/convert', methods=['POST'])
def convert_file():
    """Convert uploaded file using provided schema."""
    try:
        # Check for file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get schema
        schema_data = request.form.get('schema')
        if not schema_data:
            return jsonify({'error': 'No schema provided'}), 400
        
        try:
            schema = json.loads(schema_data)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid schema JSON'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamp + filename)
        file.save(input_path)
        
        # Convert
        parser = FixedWidthParser(schema)
        records = parser.parse_file(input_path)
        
        # Save output
        output_filename = os.path.splitext(filename)[0] + '.csv'
        output_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_timestamp + output_filename)
        
        save_to_csv(records, output_path)
        
        # Return download link
        return jsonify({
            'success': True,
            'message': f'Successfully converted {len(records)} records',
            'record_count': len(records),
            'output_file': output_timestamp + output_filename,
            'output_path': output_path
        })
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download converted CSV file."""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Security check
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename.split('_', 3)[3] if '_' in filename else filename
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate_schema', methods=['POST'])
def validate_schema():
    """Validate schema JSON."""
    try:
        schema_data = request.json.get('schema')
        if not schema_data:
            return jsonify({'valid': False, 'error': 'No schema provided'})
        
        schema = json.loads(schema_data) if isinstance(schema_data, str) else schema_data
        
        # Basic validation
        if not isinstance(schema, list):
            return jsonify({'valid': False, 'error': 'Schema must be a JSON array'})
        
        required_keys = {'name', 'start', 'length'}
        for i, col in enumerate(schema):
            if not isinstance(col, dict):
                return jsonify({'valid': False, 'error': f'Column {i} is not a dict'})
            
            if not required_keys.issubset(col.keys()):
                return jsonify({'valid': False, 'error': f'Column {i} missing required keys: {required_keys}'})
            
            if not isinstance(col['start'], int) or col['start'] < 0:
                return jsonify({'valid': False, 'error': f'Column {i} has invalid start position'})
            
            if not isinstance(col['length'], int) or col['length'] <= 0:
                return jsonify({'valid': False, 'error': f'Column {i} has invalid length'})
        
        # Check for overlaps
        columns_sorted = sorted(schema, key=lambda x: x['start'])
        for i in range(len(columns_sorted) - 1):
            curr_end = columns_sorted[i]['start'] + columns_sorted[i]['length']
            next_start = columns_sorted[i + 1]['start']
            
            if curr_end > next_start:
                return jsonify({
                    'valid': False,
                    'error': f"Columns '{columns_sorted[i]['name']}' and '{columns_sorted[i+1]['name']}' overlap"
                })
        
        return jsonify({'valid': True, 'message': 'Schema is valid', 'field_count': len(schema)})
        
    except json.JSONDecodeError as e:
        return jsonify({'valid': False, 'error': f'Invalid JSON: {str(e)}'})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})


@app.route('/api/preview', methods=['POST'])
def preview_file():
    """Preview first few lines of uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        lines = []
        
        # Read first 10 lines
        for i, line in enumerate(file.stream):
            if i >= 10:
                break
            lines.append(line.decode('utf-8', errors='ignore').rstrip())
        
        return jsonify({
            'success': True,
            'lines': lines,
            'line_count': len(lines),
            'line_length': len(lines[0]) if lines else 0
        })
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract_schema', methods=['POST'])
def extract_schema():
    """Extract schema from layout specification."""
    try:
        layout_text = request.json.get('layout_text', '')
        
        if not layout_text:
            return jsonify({'error': 'No layout text provided'}), 400
        
        # Simple extraction - looks for patterns like "Position 1-20"
        import re
        
        schema = []
        lines = layout_text.strip().split('\n')
        
        for line in lines:
            # Try to extract position, name, length pattern
            match = re.search(r'(\d+)-(\d+)\s+(.+)', line)
            if match:
                start = int(match.group(1)) - 1  # Convert to 0-based
                end = int(match.group(2))
                name = match.group(3).strip()
                
                schema.append({
                    'name': name.replace(' ', '_'),
                    'start': start,
                    'length': end - start,
                    'type': 'str',
                    'trim': True
                })
        
        if schema:
            return jsonify({'success': True, 'schema': schema})
        else:
            return jsonify({'error': 'Could not extract schema from text'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
