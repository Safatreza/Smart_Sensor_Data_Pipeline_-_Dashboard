#!/usr/bin/env python3
"""
Smart Sensor Data Dashboard - Simplified Demo
============================================

A complete FastAPI application that demonstrates a smart sensor data pipeline
and dashboard. This version is designed to be run easily with minimal setup.

Features:
- Simulated sensor data generation
- Real-time data processing
- Interactive dashboard with charts
- REST API endpoints
- WebSocket for real-time updates

Usage:
    python main.py

Then open: http://localhost:8000
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from pipeline.db_utils import get_engine
from pipeline.data_utils import load_sensor_data, compute_kpis, prepare_trend_data
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Sensor Data Dashboard",
    description="A comprehensive dashboard for industrial sensor data monitoring",
    version="2.0.0"
)

# Data models
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

# Database configuration
TABLE_NAME = "sensor_readings"

def init_database():
    """Initialize the database with sample data."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Create table if not exists
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    pressure REAL NOT NULL,
                    uptime INTEGER NOT NULL,
                    alert_level TEXT DEFAULT 'normal'
                )
            """))
            conn.commit()
            
            # Check if table is empty, if so populate with sample data
            count_query = text(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            result = conn.execute(count_query).fetchone()
            count = result[0] if result is not None else 0
            
            if count == 0:
                logger.info("Populating database with sample sensor data...")
                
                # Generate 100 sample records over the last 24 hours
                base_time = datetime.now() - timedelta(hours=24)
                sample_data = []
                
                for i in range(100):
                    timestamp = base_time + timedelta(minutes=i * 15)  # Every 15 minutes
                    temperature = random.uniform(20, 100)
                    pressure = random.uniform(900, 1100)
                    uptime = random.randint(1, 100)
                    alert_level = 'alert' if temperature > 90 or pressure > 1050 else 'normal'
                    
                    sample_data.append({
                        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "temperature": round(temperature, 2),
                        "pressure": round(pressure, 2),
                        "uptime": uptime,
                        "alert_level": alert_level
                    })
                
                insert_query = text(f"""
                    INSERT INTO {TABLE_NAME} (timestamp, temperature, pressure, uptime, alert_level)
                    VALUES (:timestamp, :temperature, :pressure, :uptime, :alert_level)
                """)
                conn.execute(insert_query, sample_data)
                conn.commit()
                logger.info(f"Added {len(sample_data)} sample records to database")
            else:
                logger.info(f"Database already contains {count} records. Skipping sample data population.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Sensor Data Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 0;
            margin-bottom: 30px;
        }
        .real-time-indicator {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-chart-line"></i> Smart Sensor Data Dashboard</h1>
                    <p class="mb-0">Real-time monitoring of industrial propulsion test rig sensors</p>
                </div>
                <div class="col-md-4 text-end">
                    <span class="real-time-indicator">
                        <i class="fas fa-circle"></i> LIVE DATA
                    </span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- KPI Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <h3 id="avg-temp">--</h3>
                    <p class="mb-0">Average Temperature (°C)</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <h3 id="avg-pressure">--</h3>
                    <p class="mb-0">Average Pressure (kPa)</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <h3 id="alert-count">--</h3>
                    <p class="mb-0">Alert Count</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card text-center">
                    <h3 id="uptime-hours">--</h3>
                    <p class="mb-0">Total Uptime (hours)</p>
                </div>
            </div>
        </div>

        <!-- Charts -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <h4>Temperature Trend</h4>
                    <canvas id="tempChart"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <h4>Pressure Trend</h4>
                    <canvas id="pressureChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>Date Filter</h5>
                        <input type="date" id="dateFilter" class="form-control" onchange="loadData()">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>Actions</h5>
                        <button class="btn btn-primary" onclick="loadData()">Refresh Data</button>
                        <button class="btn btn-success" onclick="downloadCSV()">Download CSV</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let tempChart, pressureChart;
        let ws;

        // Initialize charts
        function initCharts() {
            const tempCtx = document.getElementById('tempChart').getContext('2d');
            const pressureCtx = document.getElementById('pressureChart').getContext('2d');

            tempChart = new Chart(tempCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });

            pressureChart = new Chart(pressureCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Pressure (kPa)',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        // Load data from API
        async function loadData() {
            const dateFilter = document.getElementById('dateFilter').value;
            const url = dateFilter ? `/api/kpis?date=${dateFilter}` : '/api/kpis';
            
            try {
                // Load KPIs
                const kpiResponse = await fetch(url);
                const kpis = await kpiResponse.json();
                
                document.getElementById('avg-temp').textContent = kpis.avg_temp + '°C';
                document.getElementById('avg-pressure').textContent = kpis.avg_pressure + ' kPa';
                document.getElementById('alert-count').textContent = kpis.alert_count;
                document.getElementById('uptime-hours').textContent = kpis.uptime_hours + 'h';

                // Load trend data
                const trendUrl = dateFilter ? `/api/trends?date=${dateFilter}` : '/api/trends';
                const trendResponse = await fetch(trendUrl);
                const trends = await trendResponse.json();

                // Update charts
                tempChart.data.labels = trends.timestamps;
                tempChart.data.datasets[0].data = trends.temperatures;
                tempChart.update();

                pressureChart.data.labels = trends.timestamps;
                pressureChart.data.datasets[0].data = trends.pressures;
                pressureChart.update();

            } catch (error) {
                console.error('Error loading data:', error);
                alert('Error loading data. Please try again.');
            }
        }

        // Download CSV
        function downloadCSV() {
            const dateFilter = document.getElementById('dateFilter').value;
            const url = dateFilter ? `/api/download?date=${dateFilter}` : '/api/download';
            window.open(url, '_blank');
        }

        // WebSocket connection for real-time updates
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws/data`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log('Real-time data received:', data);
                // You can add real-time chart updates here
            };

            ws.onclose = function() {
                console.log('WebSocket connection closed');
                setTimeout(connectWebSocket, 5000); // Reconnect after 5 seconds
            };
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            loadData();
            connectWebSocket();
            
            // Auto-refresh every 30 seconds
            setInterval(loadData, 30000);
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to dashboard."""
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Render the dashboard HTML."""
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/kpis", response_model=KPIResponse)
async def get_kpis(date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """Get Key Performance Indicators for sensor data."""
    try:
        df = load_sensor_data(TABLE_NAME, date)
        kpis = compute_kpis(df)
        
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
        
    except Exception as e:
        logger.error(f"Error in KPI endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/trends", response_model=TrendResponse)
async def get_trends(date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """Get trend data for sensor visualization."""
    try:
        df = load_sensor_data(TABLE_NAME, date)
        trend_data = prepare_trend_data(df)
        
        response = TrendResponse(
            timestamps=trend_data['timestamps'],
            temperatures=trend_data['temperatures'],
            pressures=trend_data['pressures'],
            uptime_hours=trend_data['uptime_hours'],
            date_filter=date,
            record_count=trend_data['record_count']
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in trends endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            count_query = text(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            result = conn.execute(count_query).fetchone()
            record_count = result[0] if result is not None else 0
        
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

@app.get("/api/download")
async def download_csv(date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD format")):
    """Download sensor data as CSV."""
    try:
        df = load_sensor_data(TABLE_NAME, date)
        
        # Convert DataFrame to CSV
        csv_content = df.to_csv(index=False)
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sensor_data_{date or 'all'}.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download CSV: {str(e)}")

@app.websocket("/ws/data")
async def websocket_data(websocket: WebSocket):
    """WebSocket endpoint for real-time data updates."""
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

def main():
    """Main function to run the FastAPI application."""
    print("🚀 Smart Sensor Data Dashboard")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    init_database()
    
    print("✅ Database initialized successfully!")
    print("\n🌐 Starting FastAPI server...")
    print("📱 Dashboard will be available at: http://localhost:8000")
    print("🔗 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main() 