"""
Fixed-Width ASCII Tax Roll to CSV Converter
============================================
Converts fixed-width ASCII format tax roll data into clean CSV files.

Usage:
    python fixed_width_to_csv.py <input_file> <output_file> [--schema schema.json]
"""

import csv
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FixedWidthParser:
    """Parse fixed-width ASCII files based on column definitions."""
    
    def __init__(self, schema: List[Dict[str, Any]]):
        """
        Initialize parser with column schema.
        
        Args:
            schema: List of column definitions with keys:
                    - name: Column header name
                    - start: Starting position (0-indexed)
                    - length: Field width in characters
                    - type: Optional data type ('str', 'int', 'float', 'date')
                    - trim: Optional boolean to trim whitespace (default: True)
        """
        self.schema = schema
        self._validate_schema()
    
    def _validate_schema(self) -> None:
        """Validate schema definitions."""
        for i, col in enumerate(self.schema):
            if 'name' not in col or 'start' not in col or 'length' not in col:
                raise ValueError(f"Column {i} missing required fields: name, start, length")
            if col['start'] < 0 or col['length'] < 0:
                raise ValueError(f"Column '{col['name']}' has invalid start/length values")
    
    def parse_line(self, line: str) -> Dict[str, Any]:
        """
        Extract fields from a fixed-width line.
        
        Args:
            line: Single line from fixed-width file
            
        Returns:
            Dictionary with column names as keys and parsed values
        """
        record = {}
        
        for col in self.schema:
            name = col['name']
            start = col['start']
            length = col['length']
            col_type = col.get('type', 'str').lower()
            trim = col.get('trim', True)
            
            # Extract the field value
            end = start + length
            value = line[start:end] if start < len(line) else ''
            
            # Trim whitespace if requested
            if trim and col_type == 'str':
                value = value.strip()
            
            # Type conversion
            try:
                if col_type == 'int':
                    record[name] = int(value) if value.strip() else None
                elif col_type == 'float':
                    record[name] = float(value) if value.strip() else None
                elif col_type == 'date':
                    # Keep as string - can be converted to proper date if needed
                    record[name] = value.strip()
                else:  # 'str' or default
                    record[name] = value
            except ValueError as e:
                logger.warning(f"Type conversion error for column '{name}': {e}")
                record[name] = value
        
        return record
    
    def parse_file(self, input_file: str) -> List[Dict[str, Any]]:
        """
        Parse entire fixed-width file.
        
        Args:
            input_file: Path to input file
            
        Returns:
            List of dictionaries, one per record
        """
        records = []
        
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Remove newline characters
                    line = line.rstrip('\n\r')
                    
                    # Parse the line
                    record = self.parse_line(line)
                    records.append(record)
                    
                    if line_num % 10000 == 0:
                        logger.info(f"Processed {line_num} lines...")
            
            logger.info(f"Successfully parsed {len(records)} records")
            return records
        
        except FileNotFoundError:
            logger.error(f"Input file not found: {input_file}")
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            raise


def save_to_csv(records: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save parsed records to CSV file.
    
    Args:
        records: List of record dictionaries
        output_file: Path to output CSV file
    """
    if not records:
        logger.warning("No records to save")
        return
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(records[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(records)
        
        logger.info(f"CSV successfully saved to: {output_file}")
        logger.info(f"Total records written: {len(records)}")
    
    except Exception as e:
        logger.error(f"Error saving CSV: {e}")
        raise


def load_schema(schema_file: str) -> List[Dict[str, Any]]:
    """
    Load column schema from JSON file.
    
    Args:
        schema_file: Path to JSON schema file
        
    Returns:
        List of column definitions
    """
    try:
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        logger.info(f"Loaded schema from: {schema_file}")
        return schema
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in schema file: {e}")
        raise


def create_sample_schema(output_file: str = 'sample_schema.json') -> None:
    """
    Create a sample schema file for reference.
    
    Args:
        output_file: Path to save sample schema
    """
    sample_schema = [
        {
            "name": "Parcel_Number",
            "start": 0,
            "length": 18,
            "type": "str",
            "trim": True
        },
        {
            "name": "Owner_Name",
            "start": 18,
            "length": 40,
            "type": "str",
            "trim": True
        },
        {
            "name": "Property_Address",
            "start": 58,
            "length": 35,
            "type": "str",
            "trim": True
        },
        {
            "name": "Land_Use_Code",
            "start": 93,
            "length": 3,
            "type": "str",
            "trim": True
        },
        {
            "name": "Assessed_Value",
            "start": 96,
            "length": 10,
            "type": "int",
            "trim": True
        },
        {
            "name": "Tax_Amount",
            "start": 106,
            "length": 12,
            "type": "float",
            "trim": True
        },
        {
            "name": "Tax_Year",
            "start": 118,
            "length": 4,
            "type": "int",
            "trim": True
        },
        {
            "name": "Delinquent_Flag",
            "start": 122,
            "length": 1,
            "type": "str",
            "trim": True
        }
    ]
    
    with open(output_file, 'w') as f:
        json.dump(sample_schema, f, indent=2)
    
    logger.info(f"Sample schema created: {output_file}")


def main():
    """Main entry point for the converter."""
    parser = argparse.ArgumentParser(
        description='Convert fixed-width ASCII files to CSV format'
    )
    
    parser.add_argument(
        'input_file',
        help='Path to input fixed-width ASCII file'
    )
    parser.add_argument(
        'output_file',
        help='Path to output CSV file'
    )
    parser.add_argument(
        '--schema',
        default='schema.json',
        help='Path to schema JSON file (default: schema.json)'
    )
    parser.add_argument(
        '--create-sample-schema',
        action='store_true',
        help='Create a sample schema file and exit'
    )
    
    args = parser.parse_args()
    
    # Create sample schema if requested
    if args.create_sample_schema:
        create_sample_schema()
        return 0
    
    try:
        # Load schema
        schema = load_schema(args.schema)
        
        # Create parser
        parser_obj = FixedWidthParser(schema)
        
        # Parse input file
        logger.info(f"Parsing input file: {args.input_file}")
        records = parser_obj.parse_file(args.input_file)
        
        # Save to CSV
        logger.info(f"Saving to CSV: {args.output_file}")
        save_to_csv(records, args.output_file)
        
        logger.info("Conversion completed successfully!")
        return 0
    
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
