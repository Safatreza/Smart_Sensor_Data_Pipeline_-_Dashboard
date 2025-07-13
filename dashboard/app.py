"""
Smart Sensor Data Dashboard - FastAPI Application

A FastAPI-based interactive dashboard for sensor data visualization and analysis.
Provides REST API endpoints and web interface for monitoring sensor data.

Author: Smart Sensor Data Dashboard Team
Version: 2.0.0
"""

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pydantic import BaseModel
import asyncio
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Sensor Dashboard",
    description="Interactive dashboard for sensor data visualization and analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Mount static files (if any)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Database configuration
DB_PATH = "../data/processed.db"
TABLE_NAME = "sensor_data"


class KPIResponse(BaseModel):
    """Response model for KPI data."""
    avg_temp: float
    avg_pressure: float
    alert_count: int
    uptime_hours: int
    total_records: int
    date_filter: Optional[str] = None
    timestamp: str


class TrendResponse(BaseModel):
    """Response model for trend data."""
    timestamps: List[str]
    temperatures: List[float]
    pressures: List[float]
    uptime_hours: List[int]
    date_filter: Optional[str] = None
    record_count: int


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        SQLite database connection
        
    Raises:
        HTTPException: If database connection fails
    """
    try:
        if not os.path.exists(DB_PATH):
            logger.error(f"Database file not found at {DB_PATH}")
            raise HTTPException(
                status_code=500,
                detail=f"Database not found at {DB_PATH}. Please run the ETL pipeline first."
            )
        
        conn = sqlite3.connect(DB_PATH, timeout=30.0)  # Add timeout for busy database
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        cursor.close()
        
        if not tables:
            logger.warning("Database exists but contains no tables")
            
        return conn
        
    except sqlite3.OperationalError as e:
        logger.error(f"SQLite operational error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database operational error: {str(e)}"
        )
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected database connection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )


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


def load_data(date_filter: Optional[str] = None) -> pd.DataFrame:
    """
    Load sensor data from SQLite database with optional date filtering.
    
    Args:
        date_filter: Optional date filter in YYYY-MM-DD format
        
    Returns:
        DataFrame containing sensor data
        
    Raises:
        HTTPException: If database query fails or date format is invalid
    """
    conn = None
    try:
        # Validate date filter if provided
        if date_filter and not validate_date_format(date_filter):
            logger.warning(f"Invalid date format provided: {date_filter}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: {date_filter}. Use YYYY-MM-DD format."
            )
        
        conn = get_db_connection()
        
        # Check if table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (TABLE_NAME,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            logger.error(f"Table {TABLE_NAME} not found in database")
            raise HTTPException(
                status_code=500,
                detail=f"Table {TABLE_NAME} not found. Please run the ETL pipeline first."
            )
        cursor.close()
        
        # Build query with optional date filter
        if date_filter:
            query = f"""
                SELECT * FROM {TABLE_NAME}
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp
            """
            df = pd.read_sql_query(query, conn, params=[date_filter])
        else:
            query = f"SELECT * FROM {TABLE_NAME} ORDER BY timestamp"
            df = pd.read_sql_query(query, conn)
        
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
    except sqlite3.Error as e:
        logger.error(f"SQLite error in load_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load data: {str(e)}"
        )
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")


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
        # Handle timestamp column - convert to datetime if it's a string
        if 'timestamp' in df.columns:
            if df['timestamp'].dtype == 'object':  # String type
                # Convert string timestamps to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            timestamps = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        else:
            timestamps = []
        
        # Extract numeric data
        temperatures = df['temperature'].round(2).tolist() if 'temperature' in df.columns else []
        pressures = df['pressure'].round(2).tolist() if 'pressure' in df.columns else []
        uptime_hours = df['uptime'].tolist() if 'uptime' in df.columns else []
        
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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint - redirect to dashboard.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML response redirecting to dashboard
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")


@app.get("/api/kpis", response_model=KPIResponse)
async def get_kpis(date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """
    Get Key Performance Indicators for sensor data.
    
    Args:
        date: Optional date filter for specific date data
        
    Returns:
        JSON response with computed KPIs
        
    Raises:
        HTTPException: If data loading or KPI computation fails
    """
    try:
        # Load data with optional date filter
        df = load_data(date)
        
        # Compute KPIs
        kpis = compute_kpis(df)
        
        # Prepare response
        response = KPIResponse(
            avg_temp=kpis['avg_temp'],
            avg_pressure=kpis['avg_pressure'],
            alert_count=kpis['alert_count'],
            uptime_hours=kpis['uptime_hours'],
            total_records=kpis['total_records'],
            date_filter=date,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in KPI endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/trends", response_model=TrendResponse)
async def get_trends(date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """
    Get trend data for sensor visualization.
    
    Args:
        date: Optional date filter for specific date data
        
    Returns:
        JSON response with trend data
        
    Raises:
        HTTPException: If data loading or trend preparation fails
    """
    try:
        # Load data with optional date filter
        df = load_data(date)
        
        # Prepare trend data
        trend_data = prepare_trend_data(df)
        
        # Prepare response
        response = TrendResponse(
            timestamps=trend_data['timestamps'],
            temperatures=trend_data['temperatures'],
            pressures=trend_data['pressures'],
            uptime_hours=trend_data['uptime_hours'],
            date_filter=date,
            record_count=trend_data['record_count']
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trends endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with system health status
    """
    try:
        # Check database connectivity
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        record_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "record_count": record_count,
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }


@app.websocket("/ws/data")
async def websocket_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data streaming.
    Simulates new sensor readings every 5 seconds and sends them to the client.
    """
    await websocket.accept()
    try:
        while True:
            # Simulate new sensor data (could also pull from DB or cache)
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": round(random.uniform(20, 100), 2),
                "pressure": round(random.uniform(900, 1100), 2)
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)  # Send update every 5 seconds
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """
    Render the main dashboard page.
    
    Args:
        request: FastAPI request object
        date: Optional date filter for specific date data
        
    Returns:
        HTML response with rendered dashboard
        
    Raises:
        HTTPException: If data loading or template rendering fails
    """
    try:
        # Check if template exists
        template_path = os.path.join("templates", "dashboard.html")
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            raise HTTPException(
                status_code=500,
                detail="Dashboard template not found. Please ensure templates/dashboard.html exists."
            )
        
        # Load data with optional date filter
        df = load_data(date)
        
        # Compute KPIs
        kpis = compute_kpis(df)
        
        # Prepare trend data
        trend_data = prepare_trend_data(df)
        
        # Prepare template context
        context = {
            "request": request,
            "kpis": kpis,
            "trend_data": trend_data,
            "date_filter": date,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_base_url": request.base_url
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render dashboard: {str(e)}"
        )


@app.get("/api/summary")
async def get_summary():
    """
    Get comprehensive data summary including KPIs and trends.
    
    Returns:
        JSON response with complete data summary
    """
    try:
        # Load all data
        df = load_data()
        
        # Compute KPIs
        kpis = compute_kpis(df)
        
        # Prepare trend data
        trend_data = prepare_trend_data(df)
        
        # Get date range
        date_range = {
            "start": df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
            "end": df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        summary = {
            "kpis": kpis,
            "trends": trend_data,
            "date_range": date_range,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in summary endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 404,
            "message": "Page not found",
            "details": "The requested resource was not found on this server."
        },
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "message": "Internal server error",
            "details": "An unexpected error occurred. Please try again later."
        },
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = "0.0.0.0"
    port = 8000
    reload = True  # Enable auto-reload for development
    
    print("🚀 Starting Smart Sensor Dashboard - FastAPI")
    print("=" * 50)
    print(f"📊 Dashboard URL: http://{host}:{port}/dashboard")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/api/health")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 