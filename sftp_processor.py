#!/usr/bin/env python
"""
SFTP Tax Roll Downloader & Converter
====================================

Automated workflow to download tax roll files from SFTP and convert them.

Prerequisites:
- pip install paramiko  (for SFTP support)
- SFTP credentials from the data provider
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

# Uncomment to enable SFTP support
# import paramiko
# from paramiko.ssh_exception import AuthenticationException

from fixed_width_to_csv import FixedWidthParser, save_to_csv, load_schema


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SFTPTaxRollProcessor:
    """
    Download and convert tax roll files from SFTP source.
    """
    
    def __init__(self, config_file: str = 'sftp_config.json'):
        """
        Initialize with SFTP configuration.
        
        Args:
            config_file: Path to JSON config with SFTP credentials
        """
        self.config = self._load_config(config_file)
        self.schema = None
    
    def _load_config(self, config_file: str) -> dict:
        """Load SFTP configuration from JSON file."""
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ['sftp_host', 'sftp_user', 'sftp_password', 'remote_path', 'local_path', 'schema_file']
        if not all(key in config for key in required_keys):
            raise ValueError(f"Config must contain: {required_keys}")
        
        logger.info("Configuration loaded successfully")
        return config
    
    def download_file(self, remote_filename: str) -> Optional[str]:
        """
        Download file from SFTP server.
        
        NOTE: Requires 'paramiko' library. Install with: pip install paramiko
        
        Args:
            remote_filename: Name of file on SFTP server
            
        Returns:
            Local path to downloaded file, or None if failed
        """
        try:
            import paramiko
        except ImportError:
            logger.error("paramiko not installed. Install with: pip install paramiko")
            return None
        
        local_path = Path(self.config['local_path'])
        local_path.mkdir(parents=True, exist_ok=True)
        
        local_file = local_path / remote_filename
        remote_file = f"{self.config['remote_path'].rstrip('/')}/{remote_filename}"
        
        try:
            # Create SFTP connection
            transport = paramiko.Transport((self.config['sftp_host'], 22))
            transport.connect(
                username=self.config['sftp_user'],
                password=self.config['sftp_password']
            )
            
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            # Download file
            logger.info(f"Downloading {remote_file}...")
            sftp.get(remote_file, str(local_file))
            logger.info(f"Download complete: {local_file}")
            
            sftp.close()
            transport.close()
            
            return str(local_file)
        
        except Exception as e:
            logger.error(f"SFTP download failed: {e}")
            return None
    
    def list_remote_files(self) -> list:
        """
        List files available on SFTP server.
        
        Returns:
            List of filenames on remote server
        """
        try:
            import paramiko
        except ImportError:
            logger.error("paramiko not installed. Install with: pip install paramiko")
            return []
        
        try:
            transport = paramiko.Transport((self.config['sftp_host'], 22))
            transport.connect(
                username=self.config['sftp_user'],
                password=self.config['sftp_password']
            )
            
            sftp = paramiko.SFTPClient.from_transport(transport)
            files = sftp.listdir(self.config['remote_path'])
            
            sftp.close()
            transport.close()
            
            return files
        
        except Exception as e:
            logger.error(f"Failed to list remote files: {e}")
            return []
    
    def convert_file(self, input_file: str, output_file: str) -> Optional[int]:
        """
        Convert fixed-width file to CSV.
        
        Args:
            input_file: Path to input file
            output_file: Path to output CSV file
            
        Returns:
            Number of records converted, or None if failed
        """
        try:
            # Load schema
            self.schema = load_schema(self.config['schema_file'])
            
            # Parse and convert
            parser = FixedWidthParser(self.schema)
            records = parser.parse_file(input_file)
            
            # Save output
            save_to_csv(records, output_file)
            
            logger.info(f"Conversion complete: {output_file} ({len(records)} records)")
            return len(records)
        
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None
    
    def process_full_roll(self) -> Tuple[bool, str]:
        """
        Download and convert full tax roll file.
        
        Returns:
            Tuple of (success: bool, output_file: str)
        """
        filename = self.config.get('full_roll_filename', 'full_tax_roll.txt')
        
        # Download
        local_file = self.download_file(filename)
        if not local_file:
            return False, ""
        
        # Convert
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_file = f"full_tax_roll_{date_str}.csv"
        
        records = self.convert_file(local_file, output_file)
        if records is None:
            return False, ""
        
        return True, output_file
    
    def process_delinquent_roll(self) -> Tuple[bool, str]:
        """
        Download and convert delinquent tax roll file.
        
        Returns:
            Tuple of (success: bool, output_file: str)
        """
        filename = self.config.get('delinquent_roll_filename', 'delinquent_roll.txt')
        
        # Download
        local_file = self.download_file(filename)
        if not local_file:
            return False, ""
        
        # Convert
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_file = f"delinquent_roll_{date_str}.csv"
        
        records = self.convert_file(local_file, output_file)
        if records is None:
            return False, ""
        
        return True, output_file


# =============================================================================
# Configuration Template
# =============================================================================

def create_sample_config():
    """Create a sample SFTP configuration file."""
    sample_config = {
        "sftp_host": "sftp.taxassessor.example.com",
        "sftp_user": "your_username",
        "sftp_password": "your_password",  # Or use SSH key in production
        "remote_path": "/public/tax_rolls",
        "local_path": "./downloads",
        "schema_file": "schema.json",
        "full_roll_filename": "full_tax_roll.txt",
        "delinquent_roll_filename": "delinquent_roll.txt"
    }
    
    with open('sftp_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("✓ Created sample configuration: sftp_config.json")
    print("  Edit with your SFTP credentials before using.")


# =============================================================================
# Usage Examples
# =============================================================================

def example_list_files():
    """List available files on SFTP server."""
    print("Connecting to SFTP server...")
    processor = SFTPTaxRollProcessor('sftp_config.json')
    
    files = processor.list_remote_files()
    print(f"\nAvailable files on server:")
    for file in files:
        print(f"  - {file}")


def example_download_and_convert():
    """Download and convert both rolls."""
    print("Starting tax roll processing...")
    
    processor = SFTPTaxRollProcessor('sftp_config.json')
    
    # Process full roll
    print("\n1. Processing full tax roll...")
    success, output = processor.process_full_roll()
    if success:
        print(f"   ✓ Success: {output}")
    else:
        print(f"   ✗ Failed")
    
    # Process delinquent roll
    print("\n2. Processing delinquent roll...")
    success, output = processor.process_delinquent_roll()
    if success:
        print(f"   ✓ Success: {output}")
    else:
        print(f"   ✗ Failed")


def example_custom_processing():
    """Download and perform custom processing."""
    processor = SFTPTaxRollProcessor('sftp_config.json')
    
    # List available files
    files = processor.list_remote_files()
    
    # Process specific file
    if 'tax_roll_2024.txt' in files:
        local_file = processor.download_file('tax_roll_2024.txt')
        
        if local_file:
            # Custom conversion with filtering
            schema = load_schema('schema.json')
            parser = FixedWidthParser(schema)
            
            records = parser.parse_file(local_file)
            
            # Filter: only records with tax > 5000
            high_value = [r for r in records if r.get('Tax_Amount', 0) > 5000]
            
            save_to_csv(high_value, 'high_value_properties.csv')
            print(f"Processed {len(high_value)} high-value properties")


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 70)
    print("SFTP TAX ROLL PROCESSOR")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'config':
            create_sample_config()
        elif command == 'list':
            example_list_files()
        elif command == 'download':
            example_download_and_convert()
        elif command == 'custom':
            example_custom_processing()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python sftp_processor.py config     - Create sample config")
            print("  python sftp_processor.py list       - List remote files")
            print("  python sftp_processor.py download   - Download and convert")
            print("  python sftp_processor.py custom     - Custom processing")
    else:
        print("\nUsage:")
        print("  python sftp_processor.py config     - Create sample config")
        print("  python sftp_processor.py list       - List remote files")
        print("  python sftp_processor.py download   - Download and convert")
        print("  python sftp_processor.py custom     - Custom processing")
        print("\nFirst, create a config file:")
        print("  python sftp_processor.py config")
