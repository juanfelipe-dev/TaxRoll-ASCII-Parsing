"""
Usage Examples - Fixed-Width Tax Roll Converter
================================================

This file demonstrates practical ways to use the converter
in different scenarios.
"""

from fixed_width_to_csv import FixedWidthParser, save_to_csv, load_schema
import json


# =============================================================================
# Example 1: Basic Command-Line Style Usage
# =============================================================================

def example_1_basic_conversion():
    """
    Simple conversion process - the most common use case.
    """
    print("Example 1: Basic Conversion")
    print("-" * 50)
    
    # Load schema from file
    schema = load_schema('schema.json')
    
    # Create parser
    parser = FixedWidthParser(schema)
    
    # Parse input file
    records = parser.parse_file('taxes_input.txt')
    
    # Save to CSV
    save_to_csv(records, 'taxes_output.csv')
    
    print(f"✓ Converted {len(records)} records\n")


# =============================================================================
# Example 2: Using the Parser Programmatically  
# =============================================================================

def example_2_programmatic_usage():
    """
    Using the parser within your own Python code with custom processing.
    """
    print("Example 2: Programmatic Usage with Custom Processing")
    print("-" * 50)
    
    # Define schema inline
    schema = [
        {"name": "Parcel_ID", "start": 0, "length": 15, "type": "str"},
        {"name": "Owner", "start": 15, "length": 40, "type": "str"},
        {"name": "Tax_Amount", "start": 55, "length": 10, "type": "float"},
    ]
    
    # Create parser with inline schema
    parser = FixedWidthParser(schema)
    
    # Parse the file
    records = parser.parse_file('input_file.txt')
    
    # Custom filtering - only records with tax amount > 1000
    filtered = [r for r in records if r['Tax_Amount'] and r['Tax_Amount'] > 1000]
    
    # Custom transformation - add computed fields
    for record in filtered:
        record['Tax_Category'] = 'High' if record['Tax_Amount'] > 5000 else 'Medium'
    
    # Save filtered results
    save_to_csv(filtered, 'filtered_output.csv')
    
    print(f"✓ Processed {len(records)} records")
    print(f"✓ Kept {len(filtered)} records with tax > 1000\n")


# =============================================================================
# Example 3: Processing Multiple Files
# =============================================================================

def example_3_batch_processing():
    """
    Convert multiple tax roll files in a batch.
    """
    print("Example 3: Batch Processing Multiple Files")
    print("-" * 50)
    
    from pathlib import Path
    
    # File pairs to process: (input, output)
    file_pairs = [
        ('full_tax_roll_2024.txt', 'full_tax_roll_2024.csv'),
        ('delinquent_roll_2024.txt', 'delinquent_roll_2024.csv'),
        ('new_properties_2024.txt', 'new_properties_2024.csv'),
    ]
    
    # Use same schema for all files
    schema = load_schema('schema.json')
    parser = FixedWidthParser(schema)
    
    # Process each file
    results = {}
    for input_file, output_file in file_pairs:
        if Path(input_file).exists():
            print(f"  Processing: {input_file}")
            records = parser.parse_file(input_file)
            save_to_csv(records, output_file)
            results[input_file] = len(records)
        else:
            print(f"  Skipping: {input_file} (not found)")
    
    # Summary
    print("\nConversion Summary:")
    for file, count in results.items():
        print(f"  {file}: {count} records")
    print()


# =============================================================================
# Example 4: Data Quality Checks
# =============================================================================

def example_4_validation_and_cleanup():
    """
    Parse, validate, and clean data with quality checks.
    """
    print("Example 4: Validation and Data Cleanup")
    print("-" * 50)
    
    schema = load_schema('schema.json')
    parser = FixedWidthParser(schema)
    records = parser.parse_file('input.txt')
    
    # Quality metrics
    stats = {
        'total': len(records),
        'with_null_parcel': 0,
        'with_null_owner': 0,
        'invalid_tax_amount': 0,
        'cleaned': 0
    }
    
    cleaned_records = []
    
    for record in records:
        # Check for required fields
        if not record.get('Parcel_Number', '').strip():
            stats['with_null_parcel'] += 1
            continue
        
        if not record.get('Owner_Name', '').strip():
            stats['with_null_owner'] += 1
            continue
        
        # Validate numeric fields
        if record.get('Tax_Amount') is None:
            stats['invalid_tax_amount'] += 1
            continue
        
        # Data is valid
        cleaned_records.append(record)
        stats['cleaned'] += 1
    
    # Save cleaned data
    save_to_csv(cleaned_records, 'cleaned_output.csv')
    
    # Print quality report
    print(f"Total records read:           {stats['total']}")
    print(f"Missing parcel number:        {stats['with_null_parcel']}")
    print(f"Missing owner name:           {stats['with_null_owner']}")
    print(f"Invalid tax amount:           {stats['invalid_tax_amount']}")
    print(f"Records passed validation:    {stats['cleaned']}")
    print(f"Pass rate:                    {stats['cleaned']/stats['total']*100:.1f}%\n")


# =============================================================================
# Example 5: Custom Schema for Delinquent Roll
# =============================================================================

def example_5_delinquent_processing():
    """
    Process delinquent tax roll with special handling.
    """
    print("Example 5: Delinquent Tax Roll Processing")
    print("-" * 50)
    
    # Schema for delinquent rolls might have different fields
    delinquent_schema = [
        {"name": "Parcel_Number", "start": 0, "length": 18, "type": "str"},
        {"name": "Owner_Name", "start": 18, "length": 40, "type": "str"},
        {"name": "Current_Tax_Due", "start": 58, "length": 12, "type": "float"},
        {"name": "Prior_Years_Due", "start": 70, "length": 12, "type": "float"},
        {"name": "Penalties_Interest", "start": 82, "length": 12, "type": "float"},
        {"name": "Total_Delinquent", "start": 94, "length": 12, "type": "float"},
        {"name": "Last_Payment_Date", "start": 106, "length": 10, "type": "str"},
    ]
    
    parser = FixedWidthParser(delinquent_schema)
    records = parser.parse_file('delinquent_roll.txt')
    
    # Add computed fields for delinquency analysis
    for record in records:
        total = (record.get('Current_Tax_Due', 0) or 0) + \
                (record.get('Prior_Years_Due', 0) or 0) + \
                (record.get('Penalties_Interest', 0) or 0)
        
        record['Total_Amount'] = total
        
        # Classify by severity
        if total > 10000:
            record['Severity'] = 'High'
        elif total > 5000:
            record['Severity'] = 'Medium'
        else:
            record['Severity'] = 'Low'
    
    # Filter and save high-priority delinquencies
    high_priority = [r for r in records if r['Severity'] == 'High']
    
    save_to_csv(high_priority, 'delinquent_high_priority.csv')
    print(f"✓ Found {len(high_priority)} high-priority delinquencies\n")


# =============================================================================
# Example 6: Incremental Processing (for Weekly Updates)
# =============================================================================

def example_6_weekly_update():
    """
    Process weekly update files and merge with existing data.
    """
    print("Example 6: Weekly Update Processing")
    print("-" * 50)
    
    from datetime import datetime
    import os
    
    # Configuration
    schema = load_schema('schema.json')
    parser = FixedWidthParser(schema)
    
    # Generate timestamped filename
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'tax_roll_{today}.csv'
    
    # Process new data
    print(f"Processing weekly update...")
    records = parser.parse_file('sftp_tax_roll.txt')
    
    # Save with timestamp
    save_to_csv(records, filename)
    
    # Keep archive of recent files
    archive_dir = 'archive'
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # Link to archive
    print(f"Saved: {filename}")
    print(f"Archive: {archive_dir}/{filename}")
    
    # Optional: Compare with previous week
    prev_file = 'tax_roll_latest.csv'
    if os.path.exists(prev_file):
        print(f"Changes: {len(records)} records in latest update")
    
    # Update "latest" symlink
    if os.path.exists('tax_roll_latest.csv'):
        os.remove('tax_roll_latest.csv')
    # Note: Use os.symlink or shutil.copy depending on your system
    
    print()


# =============================================================================
# Example 7: Define Custom Schema from Dictionary
# =============================================================================

def example_7_dynamic_schema():
    """
    Build schema programmatically from configuration.
    """
    print("Example 7: Dynamic Schema Creation")
    print("-" * 50)
    
    # Define field specs - easier to maintain than JSON
    fields = [
        {"name": "Parcel", "start": 0, "len": 18},
        {"name": "Owner", "start": 18, "len": 40},
        {"name": "Address", "start": 58, "len": 50},
        {"name": "Value", "start": 108, "len": 10, "dtype": "int"},
        {"name": "Tax", "start": 118, "len": 10, "dtype": "float"},
    ]
    
    # Convert to standard schema format
    schema = []
    for field in fields:
        schema.append({
            "name": field["name"],
            "start": field["start"],
            "length": field["len"],
            "type": field.get("dtype", "str"),
            "trim": True
        })
    
    # Use schema
    parser = FixedWidthParser(schema)
    records = parser.parse_file('input.txt')
    save_to_csv(records, 'output.csv')
    
    print(f"✓ Converted {len(records)} records using dynamic schema\n")


# =============================================================================
# Example 8: Error Handling and Resilience
# =============================================================================

def example_8_error_handling():
    """
    Robust error handling for production use.
    """
    print("Example 8: Error Handling")
    print("-" * 50)
    
    import logging
    
    # Set up logging
    logging.basicConfig(
        filename='tax_conversion.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        schema = load_schema('schema.json')
        parser = FixedWidthParser(schema)
        
        input_file = 'input.txt'
        output_file = 'output.csv'
        
        try:
            records = parser.parse_file(input_file)
            logger.info(f"Successfully parsed {len(records)} records")
        except FileNotFoundError as e:
            logger.error(f"Input file not found: {input_file}")
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            raise
        
        try:
            save_to_csv(records, output_file)
            logger.info(f"Successfully saved CSV to {output_file}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise
        
        print("✓ Conversion completed successfully")
        print(f"  Check 'tax_conversion.log' for details\n")
        
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print(f"✗ Conversion failed. See log for details.")


# =============================================================================
# Main - Run Examples
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("FIXED-WIDTH TAX ROLL CONVERTER - USAGE EXAMPLES")
    print("=" * 70)
    print()
    
    # Uncomment the example(s) you want to run:
    
    # example_1_basic_conversion()
    # example_2_programmatic_usage()
    # example_3_batch_processing()
    # example_4_validation_and_cleanup()
    # example_5_delinquent_processing()
    # example_6_weekly_update()
    # example_7_dynamic_schema()
    # example_8_error_handling()
    
    print("=" * 70)
    print("To run an example, uncomment it in the 'if __name__' section")
    print("=" * 70)
