"""
Data Utilities for Smart Sensor Dashboard

Shared utility functions for data processing, KPI calculation, and trend preparation.
Consolidated to eliminate code duplication across the project.

Author: Smart Sensor Data Dashboard Team
Version: 2.0.0
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute Key Performance Indicators from sensor data.
    
    Args:
        df: DataFrame containing sensor data
        
    Returns:
        Dictionary containing computed KPIs
    """
    try:
        # Basic statistics
        avg_temp = df['temperature'].mean() if 'temperature' in df.columns else 0.0
        avg_pressure = df['pressure'].mean() if 'pressure' in df.columns else 0.0
        total_records = len(df)
        
        # Alert counting
        alert_count = 0
        if 'temperature_alert' in df.columns:
            alert_count += (df['temperature_alert'] == 'red').sum()
        if 'pressure_alert' in df.columns:
            alert_count += (df['pressure_alert'] == 'red').sum()
        
        # Uptime calculation
        uptime_hours = df['uptime'].max() if 'uptime' in df.columns else 0
        
        # Data quality metrics
        data_quality_score = 100.0  # Can be enhanced with more sophisticated metrics
        
        kpis = {
            'avg_temp': round(avg_temp, 2),
            'avg_pressure': round(avg_pressure, 2),
            'alert_count': int(alert_count),
            'uptime_hours': int(uptime_hours),
            'total_records': total_records,
            'data_quality_score': data_quality_score,
            'temperature_range': {
                'min': round(df['temperature'].min(), 2) if 'temperature' in df.columns else 0,
                'max': round(df['temperature'].max(), 2) if 'temperature' in df.columns else 0
            },
            'pressure_range': {
                'min': round(df['pressure'].min(), 2) if 'pressure' in df.columns else 0,
                'max': round(df['pressure'].max(), 2) if 'pressure' in df.columns else 0
            }
        }
        
        logger.info(f"KPIs computed: avg_temp={kpis['avg_temp']}°C, "
                   f"alerts={kpis['alert_count']}, uptime={kpis['uptime_hours']}h")
        
        return kpis
        
    except Exception as e:
        logger.error(f"Error computing KPIs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute KPIs: {str(e)}"
        )


def prepare_trend_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepare trend data for visualization.
    
    Args:
        df: DataFrame containing sensor data
        
    Returns:
        Dictionary containing trend data lists and metadata
    """
    try:
        if df.empty:
            return {
                'timestamps': [],
                'temperatures': [],
                'pressures': [],
                'uptime_hours': [],
                'record_count': 0
            }
        
        # Handle timestamp column - convert to datetime if it's a string
        if 'timestamp' in df.columns:
            if df['timestamp'].dtype == 'object':  # String type
                # Convert string timestamps to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            timestamps = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('Unknown').tolist()
        else:
            timestamps = []
        
        # Extract numeric data with error handling
        temperatures = df['temperature'].round(2).fillna(0).tolist() if 'temperature' in df.columns else []
        pressures = df['pressure'].round(2).fillna(0).tolist() if 'pressure' in df.columns else []
        uptime_hours = df['uptime'].fillna(0).tolist() if 'uptime' in df.columns else []
        
        trend_data = {
            'timestamps': timestamps,
            'temperatures': temperatures,
            'pressures': pressures,
            'uptime_hours': uptime_hours,
            'record_count': len(df)
        }
        
        logger.info(f"Trend data prepared: {len(timestamps)} data points")
        return trend_data
        
    except Exception as e:
        logger.error(f"Error preparing trend data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prepare trend data: {str(e)}"
        )


def load_sensor_data(table_name: str, date_filter: Optional[str] = None) -> pd.DataFrame:
    """
    Load sensor data from the configured database with optional date filtering.
    
    Args:
        table_name: Name of the database table
        date_filter: Optional date filter in YYYY-MM-DD format
        
    Returns:
        DataFrame containing sensor data
        
    Raises:
        HTTPException: If database query fails or date format is invalid
    """
    from pipeline.db_utils import get_engine
    
    engine = get_engine()
    try:
        # Validate date filter if provided
        if date_filter and not validate_date_format(date_filter):
            logger.warning(f"Invalid date format provided: {date_filter}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: {date_filter}. Use YYYY-MM-DD format."
            )
        
        # Build query with optional date filter
        if date_filter:
            query = f"SELECT * FROM {table_name} WHERE DATE(timestamp) = :date ORDER BY timestamp"
            df = pd.read_sql(query, engine, params={"date": date_filter})
        else:
            query = f"SELECT * FROM {table_name} ORDER BY timestamp"
            df = pd.read_sql(query, engine)
        
        if df.empty:
            if date_filter:
                logger.warning(f"No data found for date: {date_filter}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for date: {date_filter}"
                )
            else:
                logger.error("No data found in database")
                raise HTTPException(
                    status_code=404,
                    detail="No data found in database. Please run the ETL pipeline first."
                )
        
        logger.info(f"Loaded {len(df)} records from database")
        return df
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in load_sensor_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        ) 