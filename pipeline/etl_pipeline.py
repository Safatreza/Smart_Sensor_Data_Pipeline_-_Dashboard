"""
Industrial Sensor Data ETL Pipeline

A modular ETL pipeline for processing industrial sensor data (temperature, pressure, uptime)
with anomaly detection and KPI calculations. Designed for propulsion test rigs and similar
industrial systems.

Author: Smart Sensor Data Dashboard Team
Version: 2.0.0
"""

import pandas as pd
import os
import random
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import math
from pipeline.db_utils import get_engine, is_postgres, create_timescale_hypertable
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration section - load from .env file if present, otherwise use defaults
def load_config() -> Dict[str, str]:
    """
    Load configuration variables from .env file or use defaults.
    
    Returns:
        Dict containing configuration variables
    """
    config = {
        'DATA_PATH': '../data/simulated_raw.csv',
        'DB_PATH': '../data/processed.db',
        'TABLE_NAME': 'sensor_data',
        'PROCESSED_DATA_PATH': '../data/simulated_processed.csv'
    }
    
    # Try to load from .env file
    env_file = '.env'
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
            logger.info(f"Configuration loaded from {env_file}")
        except Exception as e:
            logger.warning(f"Could not load .env file: {e}. Using defaults.")
    else:
        logger.info("No .env file found. Using default configuration.")
    
    return config

# Load configuration
CONFIG = load_config()

def extract_data(num_rows: int = 100) -> pd.DataFrame:
    """
    Extract sensor data from CSV file or generate mock data if file doesn't exist.
    Generates num_rows of industrial sensor data.
    """
    data_path = CONFIG['DATA_PATH']
    
    # Check if data file exists
    if os.path.exists(data_path):
        try:
            logger.info(f"Reading existing data from {data_path}")
            df = pd.read_csv(data_path)
            
            # Validate the DataFrame structure
            required_columns = ['timestamp', 'temperature', 'pressure', 'uptime']
            if not all(col in df.columns for col in required_columns):
                logger.warning(f"CSV file missing required columns. Expected: {required_columns}")
                logger.info("Generating new mock data instead.")
            else:
                logger.info(f"Successfully loaded {len(df)} records from {data_path}")
                return df
        except FileNotFoundError:
            logger.error(f"Data file not found: {data_path}")
            logger.info("Generating new mock data instead.")
        except pd.errors.EmptyDataError:
            logger.error(f"Data file is empty: {data_path}")
            logger.info("Generating new mock data instead.")
        except Exception as e:
            logger.error(f"Error reading {data_path}: {e}")
            logger.info("Generating new mock data instead.")
    
    # Generate mock industrial sensor data
    logger.info(f"Generating {num_rows} rows of mock industrial sensor data")
    
    # Create timestamp range (last 100 hours)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=num_rows - 1)
    timestamps = [start_time + timedelta(hours=i) for i in range(num_rows)]
    
    # Generate sensor data
    data = []
    for i, timestamp in enumerate(timestamps):
        # Generate realistic industrial sensor readings
        # Temperature: 20-100°C with some variation
        base_temp = 60 + 20 * math.sin(2 * math.pi * i / 24)  # Daily cycle
        temperature = base_temp + random.uniform(-10, 10)
        temperature = max(20, min(100, temperature))  # Clamp to range
        
        # Pressure: 900-1100 hPa with some variation
        base_pressure = 1000 + 50 * math.sin(2 * math.pi * i / 12)  # 12-hour cycle
        pressure = base_pressure + random.uniform(-20, 20)
        pressure = max(900, min(1100, pressure))  # Clamp to range
        
        # Uptime: Incremental hours
        uptime = i
        
        # Add some anomalies (5% chance)
        if random.random() < 0.05:
            if random.choice([True, False]):
                temperature += random.choice([-30, 30])  # Temperature spike/drop
            else:
                pressure += random.choice([-100, 100])  # Pressure spike/drop
        
        data.append({
            'timestamp': timestamp,
            'temperature': round(temperature, 2),
            'pressure': round(pressure, 2),
            'uptime': uptime
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    
    # Save raw data
    try:
        df.to_csv(data_path, index=False)
        logger.info(f"Mock data saved to {data_path}")
    except Exception as e:
        logger.error(f"Error saving mock data to {data_path}: {e}")
    
    return df

def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Transform and clean the raw sensor data using vectorized pandas operations.
    Returns (processed_df, kpis)
    """
    logger.info("Starting data transformation")
    processed_df = df.copy()
    processed_df = processed_df.dropna()
    processed_df = processed_df[(processed_df['temperature'] >= 0) & (processed_df['temperature'] <= 150)]
    processed_df = processed_df[(processed_df['pressure'] >= 800) & (processed_df['pressure'] <= 1200)]
    processed_df = pd.DataFrame(processed_df).reset_index(drop=True)
    if len(processed_df) > 0:
        temp_mean = processed_df['temperature'].mean()
        temp_std = processed_df['temperature'].std()
        processed_df['temperature_zscore'] = (processed_df['temperature'] - temp_mean) / temp_std if temp_std > 0 else 0
        pressure_mean = processed_df['pressure'].mean()
        pressure_std = processed_df['pressure'].std()
        processed_df['pressure_zscore'] = (processed_df['pressure'] - pressure_mean) / pressure_std if pressure_std > 0 else 0
    processed_df['temperature_alert'] = 'normal'
    processed_df['pressure_alert'] = 'normal'
    processed_df.loc[abs(processed_df['temperature_zscore']) > 2, 'temperature_alert'] = 'red'
    processed_df.loc[abs(processed_df['pressure_zscore']) > 2.5, 'pressure_alert'] = 'red'
    processed_df.loc[(abs(processed_df['pressure_zscore']) > 1.5) & (abs(processed_df['pressure_zscore']) <= 2.5), 'pressure_alert'] = 'yellow'
    temp_alerts = (processed_df['temperature_alert'] == 'red').sum()
    pressure_alerts = (processed_df['pressure_alert'] == 'red').sum()
    pressure_warnings = (processed_df['pressure_alert'] == 'yellow').sum()
    kpis = {
        'avg_temp': processed_df['temperature'].mean(),
        'avg_pressure': processed_df['pressure'].mean(),
        'alert_count': temp_alerts + pressure_alerts,
        'uptime_hours': processed_df['uptime'].max() if len(processed_df) > 0 else 0,
        'total_records': len(processed_df),
        'data_quality_score': len(processed_df) / len(df) * 100 if len(df) > 0 else 0
    }
    logger.info(f"KPIs calculated: avg_temp={kpis['avg_temp']:.2f}°C, avg_pressure={kpis['avg_pressure']:.2f}hPa, alert_count={kpis['alert_count']}, uptime_hours={kpis['uptime_hours']}")
    logger.info("Data transformation completed successfully")
    return processed_df, kpis

def load_data(df: pd.DataFrame) -> bool:
    """
    Load processed data into the configured database. Adds indexes for fast queries.
    """
    table_name = CONFIG['TABLE_NAME']
    try:
        if df is None or len(df) == 0:
            logger.error("Cannot load empty or None DataFrame")
            return False
        logger.info(f"Loading {len(df)} records into database table: {table_name}")
        engine = get_engine()
        # Write DataFrame to SQL database
        df.to_sql(table_name, engine, if_exists='replace', index=False, method=None)
        # Create indexes (SQLite or PostgreSQL)
        with engine.connect() as conn:
            if is_postgres():
                # TimescaleDB hypertable
                create_timescale_hypertable(table_name, time_column="timestamp")
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_timestamp ON {table_name} (timestamp)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_uptime ON {table_name} (uptime)"))
                if 'temperature_alert' in df.columns:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_temp_alert ON {table_name} (temperature_alert)"))
                if 'pressure_alert' in df.columns:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_pressure_alert ON {table_name} (pressure_alert)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_temperature ON {table_name} (temperature)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_pressure ON {table_name} (pressure)"))
            else:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_timestamp ON {table_name} (timestamp)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_uptime ON {table_name} (uptime)"))
                if 'temperature_alert' in df.columns:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_temp_alert ON {table_name} (temperature_alert)"))
                if 'pressure_alert' in df.columns:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_pressure_alert ON {table_name} (pressure_alert)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_temperature ON {table_name} (temperature)"))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_pressure ON {table_name} (pressure)"))
        logger.info(f"Successfully loaded {len(df)} records into {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error loading data into database: {e}")
        return False

def save_processed_csv(df: pd.DataFrame) -> bool:
    """
    Save processed DataFrame to CSV file for demo use.
    
    Args:
        df: Processed DataFrame to save
        
    Returns:
        True if successful, False otherwise
    """
    processed_path = CONFIG['PROCESSED_DATA_PATH']
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(processed_path, index=False)
        logger.info(f"Processed data saved to {processed_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving processed data to {processed_path}: {e}")
        return False

def get_data_summary() -> Dict:
    """
    Get summary statistics of processed data from database.
    """
    table_name = CONFIG['TABLE_NAME']
    try:
        engine = get_engine()
        summary_query = f"""
            SELECT 
                COUNT(*) as total_records,
                MIN(timestamp) as earliest_timestamp,
                MAX(timestamp) as latest_timestamp,
                AVG(temperature) as avg_temperature,
                AVG(pressure) as avg_pressure,
                MAX(uptime) as max_uptime,
                COUNT(CASE WHEN temperature_alert = 'red' THEN 1 END) as temp_alerts,
                COUNT(CASE WHEN pressure_alert = 'red' THEN 1 END) as pressure_alerts
            FROM {table_name}
        """
        summary_df = pd.read_sql(summary_query, engine)
        if len(summary_df) == 0:
            return {}
        summary = {
            'total_records': int(summary_df['total_records'].iloc[0]),
            'date_range': {
                'start': summary_df['earliest_timestamp'].iloc[0],
                'end': summary_df['latest_timestamp'].iloc[0]
            },
            'averages': {
                'temperature': float(summary_df['avg_temperature'].iloc[0]),
                'pressure': float(summary_df['avg_pressure'].iloc[0])
            },
            'uptime_hours': int(summary_df['max_uptime'].iloc[0]),
            'alerts': {
                'temperature_alerts': int(summary_df['temp_alerts'].iloc[0]),
                'pressure_alerts': int(summary_df['pressure_alerts'].iloc[0])
            }
        }
        return summary
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return {}

def run_etl(num_rows: int = 100) -> Tuple[bool, pd.DataFrame, dict]:
    """
    Orchestrate the complete ETL pipeline with timing logs for each step.
    Returns (success, processed_data, kpis)
    """
    import time
    logger.info("Starting ETL pipeline execution")
    try:
        logger.info("Step 1: Extracting data")
        t0 = time.time()
        raw_data = extract_data(num_rows)
        t1 = time.time()
        logger.info(f"Extracted {len(raw_data)} rows in {t1-t0:.2f} seconds")
        if len(raw_data) == 0:
            logger.error("No data extracted. ETL pipeline failed.")
            return False, pd.DataFrame(), {}
        logger.info("Step 2: Transforming data")
        t2 = time.time()
        processed_data, kpis = transform_data(raw_data)
        t3 = time.time()
        logger.info(f"Transformed data in {t3-t2:.2f} seconds")
        if len(processed_data) == 0:
            logger.error("No data after transformation. ETL pipeline failed.")
            return False, pd.DataFrame(), {}
        logger.info("Step 3: Loading data into database")
        t4 = time.time()
        load_success = load_data(processed_data)
        t5 = time.time()
        logger.info(f"Loaded data into database in {t5-t4:.2f} seconds")
        if not load_success:
            logger.error("Failed to load data into database.")
            return False, processed_data, kpis
        logger.info("Step 4: Saving processed data to CSV")
        t6 = time.time()
        csv_success = save_processed_csv(processed_data)
        t7 = time.time()
        logger.info(f"Saved processed CSV in {t7-t6:.2f} seconds")
        if not csv_success:
            logger.warning("Failed to save processed CSV, but database load was successful.")
        summary = get_data_summary()
        if summary:
            logger.info(f"ETL pipeline completed successfully!")
            logger.info(f"  - Total records: {summary['total_records']}")
            logger.info(f"  - Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
            logger.info(f"  - Average temperature: {summary['averages']['temperature']:.2f}°C")
            logger.info(f"  - Average pressure: {summary['averages']['pressure']:.2f}hPa")
            logger.info(f"  - Uptime: {summary['uptime_hours']} hours")
            logger.info(f"  - Temperature alerts: {summary['alerts']['temperature_alerts']}")
            logger.info(f"  - Pressure alerts: {summary['alerts']['pressure_alerts']}")
        else:
            logger.warning("Could not retrieve data summary")
        return True, processed_data, kpis
    except Exception as e:
        logger.error(f"ETL pipeline failed with error: {e}")
        return False, pd.DataFrame(), {}

def main():
    """
    Main function to run the ETL pipeline when script is executed directly.
    Accepts ETL_NUM_ROWS env var or CLI arg for row count.
    """
    import os
    import sys
    logger.info("Industrial Sensor Data ETL Pipeline")
    logger.info("=" * 50)
    num_rows = 100
    if 'ETL_NUM_ROWS' in os.environ:
        try:
            num_rows = int(os.environ['ETL_NUM_ROWS'])
        except Exception:
            pass
    if len(sys.argv) > 1:
        try:
            num_rows = int(sys.argv[1])
        except Exception:
            pass
    logger.info(f"Running ETL with {num_rows} rows")
    success, processed_data, kpis = run_etl(num_rows)
    if success:
        logger.info("ETL pipeline completed successfully!")
        if kpis:
            print("\nKey Performance Indicators:")
            print(f"  Average Temperature: {kpis['avg_temp']:.2f}°C")
            print(f"  Average Pressure: {kpis['avg_pressure']:.2f}hPa")
            print(f"  Total Alerts: {kpis['alert_count']}")
            print(f"  Uptime Hours: {kpis['uptime_hours']}")
            print(f"  Data Quality Score: {kpis['data_quality_score']:.1f}%")
            print(f"  Total Records: {kpis['total_records']}")
    else:
        logger.error("ETL pipeline failed!")
        return 1
    return 0

if __name__ == "__main__":
    exit(main()) 