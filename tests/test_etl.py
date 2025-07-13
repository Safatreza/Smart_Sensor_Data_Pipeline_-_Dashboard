"""
Unit Tests for Smart Sensor Data Pipeline ETL Functions

This module contains comprehensive tests for the ETL pipeline including:
- Data extraction from CSV files
- Data transformation and cleaning
- Database loading operations
- Error handling and edge cases

Author: Smart Sensor Data Dashboard Team
Version: 1.0.0
"""

import unittest
import tempfile
import os
import sqlite3
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
import sys
import logging

# Add the pipeline directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pipeline'))

# Import the ETL functions to test
try:
    from etl_pipeline import extract_data, transform_data, load_data, run_etl
except ImportError:
    # Fallback for testing without the actual module
    pass


class TestETLPipeline(unittest.TestCase):
    """Test cases for the ETL pipeline functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.test_dir, 'test_raw.csv')
        self.test_db_path = os.path.join(self.test_dir, 'test_processed.db')
        
        # Create sample test data
        self.sample_data = self._create_sample_data()
        
        # Set up logging to avoid console output during tests
        logging.getLogger().setLevel(logging.ERROR)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_sample_data(self):
        """Create sample sensor data for testing."""
        # Generate 100 rows of realistic sensor data
        timestamps = []
        temperatures = []
        pressures = []
        uptimes = []
        
        base_time = datetime(2025, 7, 13, 0, 0, 0)
        
        for i in range(100):
            timestamps.append(base_time + timedelta(minutes=6*i))
            temperatures.append(20 + 60 * np.sin(i * 0.1) + np.random.normal(0, 5))
            pressures.append(1000 + 50 * np.sin(i * 0.05) + np.random.normal(0, 10))
            uptimes.append(i * 0.1)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'temperature': temperatures,
            'pressure': pressures,
            'uptime': uptimes
        })
    
    def _create_test_csv(self, data=None):
        """Create a test CSV file with sample data."""
        if data is None:
            data = self.sample_data
        
        # Add header comment
        csv_content = "# Test sensor data\n"
        csv_content += "timestamp,temperature,pressure,uptime\n"
        
        # Add data rows
        for _, row in data.iterrows():
            csv_content += f"{row['timestamp']},{row['temperature']:.1f},{row['pressure']:.1f},{row['uptime']:.1f}\n"
        
        with open(self.test_csv_path, 'w') as f:
            f.write(csv_content)
    
    def test_extract_data_success(self):
        """Test successful data extraction from CSV file."""
        # Create test CSV file
        self._create_test_csv()
        
        # Mock the environment variable to point to our test file
        with patch.dict(os.environ, {'DATA_PATH': self.test_csv_path}):
            # Test the extract function
            result = extract_data()
            
            # Verify the result is a DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            
            # Verify it has the expected number of rows
            self.assertEqual(len(result), 100)
            
            # Verify it has the expected columns
            expected_columns = ['timestamp', 'temperature', 'pressure', 'uptime']
            self.assertListEqual(list(result.columns), expected_columns)
            
            # Verify data types
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['timestamp']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['temperature']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['pressure']))
            self.assertTrue(pd.api.types.is_numeric_dtype(result['uptime']))
    
    def test_extract_data_missing_file(self):
        """Test data extraction when CSV file is missing."""
        # Mock a non-existent file path
        with patch.dict(os.environ, {'DATA_PATH': '/nonexistent/file.csv'}):
            # Test that the function handles missing files gracefully
            result = extract_data()
            
            # Should return a DataFrame (fallback to simulated data)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreater(len(result), 0)
    
    def test_extract_data_empty_file(self):
        """Test data extraction with empty CSV file."""
        # Create empty CSV file
        with open(self.test_csv_path, 'w') as f:
            f.write("timestamp,temperature,pressure,uptime\n")
        
        with patch.dict(os.environ, {'DATA_PATH': self.test_csv_path}):
            result = extract_data()
            
            # Should handle empty file gracefully
            self.assertIsInstance(result, pd.DataFrame)
    
    def test_extract_data_invalid_format(self):
        """Test data extraction with invalid CSV format."""
        # Create CSV with invalid format
        with open(self.test_csv_path, 'w') as f:
            f.write("invalid,format,file\n")
            f.write("1,2,3\n")
        
        with patch.dict(os.environ, {'DATA_PATH': self.test_csv_path}):
            result = extract_data()
            
            # Should handle invalid format gracefully
            self.assertIsInstance(result, pd.DataFrame)
    
    def test_transform_data_success(self):
        """Test successful data transformation."""
        # Test with valid data
        result = transform_data(self.sample_data)
        
        # Verify the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Verify it has the expected columns (including new ones)
        expected_columns = ['timestamp', 'temperature', 'pressure', 'uptime', 
                           'z_score_temp', 'alert_status']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Verify no null values in critical columns
        self.assertFalse(result['temperature'].isnull().any())
        self.assertFalse(result['pressure'].isnull().any())
        self.assertFalse(result['uptime'].isnull().any())
        
        # Verify temperature range filtering (0-150°C)
        self.assertTrue((result['temperature'] >= 0).all())
        self.assertTrue((result['temperature'] <= 150).all())
        
        # Verify pressure range filtering (800-1200 hPa)
        self.assertTrue((result['pressure'] >= 800).all())
        self.assertTrue((result['pressure'] <= 1200).all())
        
        # Verify Z-score calculation
        self.assertTrue('z_score_temp' in result.columns)
        self.assertTrue(pd.api.types.is_numeric_dtype(result['z_score_temp']))
        
        # Verify alert status
        self.assertTrue('alert_status' in result.columns)
        self.assertTrue(result['alert_status'].isin(['red', 'green']).all())
    
    def test_transform_data_empty_dataframe(self):
        """Test transformation with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['timestamp', 'temperature', 'pressure', 'uptime'])
        
        result = transform_data(empty_df)
        
        # Should handle empty DataFrame gracefully
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)
    
    def test_transform_data_with_nulls(self):
        """Test transformation with null values."""
        # Create data with null values
        data_with_nulls = self.sample_data.copy()
        data_with_nulls.loc[0, 'temperature'] = np.nan
        data_with_nulls.loc[1, 'pressure'] = np.nan
        
        result = transform_data(data_with_nulls)
        
        # Should remove null values
        self.assertFalse(result['temperature'].isnull().any())
        self.assertFalse(result['pressure'].isnull().any())
        
        # Should have fewer rows than input (nulls removed)
        self.assertLess(len(result), len(data_with_nulls))
    
    def test_transform_data_out_of_range_values(self):
        """Test transformation with out-of-range values."""
        # Create data with out-of-range values
        data_out_of_range = self.sample_data.copy()
        data_out_of_range.loc[0, 'temperature'] = 200  # Above 150°C
        data_out_of_range.loc[1, 'temperature'] = -10  # Below 0°C
        data_out_of_range.loc[2, 'pressure'] = 1500    # Above 1200 hPa
        data_out_of_range.loc[3, 'pressure'] = 500     # Below 800 hPa
        
        result = transform_data(data_out_of_range)
        
        # Should filter out out-of-range values
        self.assertTrue((result['temperature'] >= 0).all())
        self.assertTrue((result['temperature'] <= 150).all())
        self.assertTrue((result['pressure'] >= 800).all())
        self.assertTrue((result['pressure'] <= 1200).all())
    
    def test_transform_data_z_score_calculation(self):
        """Test Z-score calculation accuracy."""
        # Create simple test data for Z-score calculation
        simple_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-13', periods=5, freq='6min'),
            'temperature': [20, 25, 30, 35, 40],
            'pressure': [1000, 1005, 1010, 1015, 1020],
            'uptime': [0.0, 0.1, 0.2, 0.3, 0.4]
        })
        
        result = transform_data(simple_data)
        
        # Verify Z-score calculation
        temp_mean = simple_data['temperature'].mean()
        temp_std = simple_data['temperature'].std()
        
        # Check a few Z-score values
        expected_z_score_0 = (20 - temp_mean) / temp_std
        self.assertAlmostEqual(result.loc[0, 'z_score_temp'], expected_z_score_0, places=2)
    
    def test_transform_data_alert_detection(self):
        """Test alert detection based on Z-score."""
        # Create data with extreme values to trigger alerts
        extreme_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-13', periods=10, freq='6min'),
            'temperature': [20, 25, 30, 35, 40, 45, 50, 55, 60, 100],  # Last value is extreme
            'pressure': [1000] * 10,
            'uptime': [i * 0.1 for i in range(10)]
        })
        
        result = transform_data(extreme_data)
        
        # Should detect alerts for extreme values
        self.assertTrue('alert_status' in result.columns)
        
        # Check if extreme values are marked as red alerts
        extreme_indices = result[result['temperature'] > 50].index
        for idx in extreme_indices:
            self.assertEqual(result.loc[idx, 'alert_status'], 'red')
    
    @patch('sqlite3.connect')
    def test_load_data_success(self, mock_connect):
        """Test successful data loading to database."""
        # Mock the database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock environment variable
        with patch.dict(os.environ, {'DB_PATH': self.test_db_path}):
            # Test the load function
            result = load_data(self.sample_data)
            
            # Verify database operations were called
            mock_connect.assert_called_once()
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()
            mock_conn.close.assert_called_once()
            
            # Verify the result contains expected information
            self.assertIsInstance(result, dict)
            self.assertIn('records_loaded', result)
            self.assertEqual(result['records_loaded'], len(self.sample_data))
    
    @patch('sqlite3.connect')
    def test_load_data_database_error(self, mock_connect):
        """Test data loading with database connection error."""
        # Mock database connection to raise an error
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        with patch.dict(os.environ, {'DB_PATH': self.test_db_path}):
            # Should handle database errors gracefully
            result = load_data(self.sample_data)
            
            # Should return error information
            self.assertIsInstance(result, dict)
            self.assertIn('error', result)
    
    def test_load_data_empty_dataframe(self):
        """Test data loading with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['timestamp', 'temperature', 'pressure', 'uptime'])
        
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            result = load_data(empty_df)
            
            # Should handle empty DataFrame gracefully
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get('records_loaded', 0), 0)
    
    @patch('pipeline.etl_pipeline.extract_data')
    @patch('pipeline.etl_pipeline.transform_data')
    @patch('pipeline.etl_pipeline.load_data')
    def test_run_etl_success(self, mock_load, mock_transform, mock_extract):
        """Test successful ETL pipeline execution."""
        # Mock the individual functions
        mock_extract.return_value = self.sample_data
        mock_transform.return_value = self.sample_data
        mock_load.return_value = {'records_loaded': 100, 'status': 'success'}
        
        # Test the complete pipeline
        result = run_etl()
        
        # Verify all functions were called
        mock_extract.assert_called_once()
        mock_transform.assert_called_once()
        mock_load.assert_called_once()
        
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn('status', result)
    
    @patch('pipeline.etl_pipeline.extract_data')
    def test_run_etl_extract_error(self, mock_extract):
        """Test ETL pipeline with extraction error."""
        # Mock extract function to raise an error
        mock_extract.side_effect = Exception("Extraction failed")
        
        # Test that the pipeline handles extraction errors
        result = run_etl()
        
        # Should return error information
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
    
    @patch('pipeline.etl_pipeline.extract_data')
    @patch('pipeline.etl_pipeline.transform_data')
    def test_run_etl_transform_error(self, mock_transform, mock_extract):
        """Test ETL pipeline with transformation error."""
        # Mock functions
        mock_extract.return_value = self.sample_data
        mock_transform.side_effect = Exception("Transformation failed")
        
        # Test that the pipeline handles transformation errors
        result = run_etl()
        
        # Should return error information
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
    
    def test_data_quality_checks(self):
        """Test data quality validation in transformation."""
        # Create data with various quality issues
        quality_test_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-13', periods=10, freq='6min'),
            'temperature': [20, np.nan, 30, -5, 35, 200, 40, 45, 50, 55],
            'pressure': [1000, 1005, np.nan, 1010, 500, 1015, 1500, 1020, 1025, 1030],
            'uptime': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        })
        
        result = transform_data(quality_test_data)
        
        # Should remove nulls and out-of-range values
        self.assertFalse(result['temperature'].isnull().any())
        self.assertFalse(result['pressure'].isnull().any())
        self.assertTrue((result['temperature'] >= 0).all())
        self.assertTrue((result['temperature'] <= 150).all())
        self.assertTrue((result['pressure'] >= 800).all())
        self.assertTrue((result['pressure'] <= 1200).all())
        
        # Should have fewer rows than input (quality issues removed)
        self.assertLess(len(result), len(quality_test_data))


class TestETLIntegration(unittest.TestCase):
    """Integration tests for the complete ETL pipeline."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.test_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.test_dir, 'test_raw.csv')
        self.test_db_path = os.path.join(self.test_dir, 'test_processed.db')
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'timestamp': pd.date_range('2025-07-13', periods=50, freq='6min'),
            'temperature': np.random.normal(30, 10, 50),
            'pressure': np.random.normal(1000, 50, 50),
            'uptime': np.arange(0, 5, 0.1)
        })
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_end_to_end_pipeline(self):
        """Test complete ETL pipeline from CSV to database."""
        # Create test CSV file
        self.sample_data.to_csv(self.test_csv_path, index=False)
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'DATA_PATH': self.test_csv_path,
            'DB_PATH': self.test_db_path,
            'TABLE_NAME': 'sensor_data'
        }):
            # Run the complete pipeline
            result = run_etl()
            
            # Verify successful execution
            self.assertIsInstance(result, dict)
            self.assertIn('status', result)
            
            # Verify database was created
            self.assertTrue(os.path.exists(self.test_db_path))
            
            # Verify data can be queried from database
            conn = sqlite3.connect(self.test_db_path)
            query_result = pd.read_sql_query("SELECT COUNT(*) as count FROM sensor_data", conn)
            conn.close()
            
            self.assertGreater(query_result['count'].iloc[0], 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 