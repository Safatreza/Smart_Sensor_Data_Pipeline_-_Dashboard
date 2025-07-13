#!/usr/bin/env python3
"""
Test script to verify demo functionality
"""

import os
import sys
import csv
from datetime import datetime

def test_csv_loading():
    """Test loading the CSV file directly"""
    csv_path = "data/simulated_processed.csv"
    
    print(f"Testing CSV loading from: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        print("❌ CSV file not found!")
        return False
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Skip comment lines
            lines = csvfile.readlines()
            data_lines = [line for line in lines if not line.strip().startswith('#')]
            
            if not data_lines:
                print("❌ No data lines found in CSV file")
                return False
            
            # Create a StringIO object for csv.DictReader
            from io import StringIO
            csv_content = StringIO(''.join(data_lines))
            reader = csv.DictReader(csv_content)
            
            # Validate required columns
            required_columns = ['timestamp', 'temperature', 'pressure', 'uptime']
            if reader.fieldnames is None:
                print("❌ CSV file has no headers")
                return False
                
            print(f"Found columns: {reader.fieldnames}")
            
            if not all(col in reader.fieldnames for col in required_columns):
                missing_cols = [col for col in required_columns if col not in reader.fieldnames]
                print(f"❌ Missing required columns: {missing_cols}")
                return False
            
            # Count rows
            row_count = 0
            alert_count = 0
            
            for row in reader:
                row_count += 1
                if 'alert_status' in row and row['alert_status'] == 'red':
                    alert_count += 1
            
            print(f"✅ Successfully loaded {row_count} rows")
            print(f"✅ Found {alert_count} alert records")
            return True
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_demo_import():
    """Test importing the demo module"""
    try:
        sys.path.append('demo')
        from run_demo import load_demo_data, generate_html
        print("✅ Demo module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing demo module: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Demo Functionality")
    print("=" * 40)
    
    # Test CSV loading
    csv_ok = test_csv_loading()
    
    # Test demo import
    import_ok = test_demo_import()
    
    if csv_ok and import_ok:
        print("\n✅ All tests passed! Demo should work correctly.")
        print("\nTo run the demo:")
        print("   python demo/run_demo.py")
    else:
        print("\n❌ Some tests failed. Please check the issues above.") 