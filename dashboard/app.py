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
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pydantic import BaseModel
import asyncio
import random
from pipeline.db_utils import get_engine
from pipeline.data_utils import load_sensor_data, compute_kpis, prepare_trend_data
from sqlalchemy import text

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
        df = load_sensor_data(TABLE_NAME, date)
        
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
        df = load_sensor_data(TABLE_NAME, date)
        
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
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
            fetch_result = result.fetchone()
            record_count = fetch_result[0] if fetch_result is not None else 0
        
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
    WebSocket endpoint for real-time data updates.
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    try:
        while True:
            # Send real-time data every 30 seconds
            await asyncio.sleep(30)
            
            # Get latest data
            df = load_sensor_data(TABLE_NAME)
            kpis = compute_kpis(df)
            
            # Send data to client
            await websocket.send_json({
                "type": "update",
                "kpis": kpis,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


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
        df = load_sensor_data(TABLE_NAME, date)
        
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
        df = load_sensor_data(TABLE_NAME)
        
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


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    Handle 404 errors.
    
    Args:
        request: FastAPI request object
        exc: HTTPException
        
    Returns:
        HTML response with error page
    """
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 404,
        "error_message": "Page not found",
        "error_description": "The requested page could not be found."
    })


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """
    Handle 500 errors.
    
    Args:
        request: FastAPI request object
        exc: HTTPException
        
    Returns:
        HTML response with error page
    """
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 500,
        "error_message": "Internal server error",
        "error_description": "An unexpected error occurred. Please try again later."
    })


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