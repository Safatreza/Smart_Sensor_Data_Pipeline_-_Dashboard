# Smart Sensor Data Pipeline & Dashboard - User Summary

## 🎯 Purpose

This project simulates an industrial sensor system (propulsion test rig) to demonstrate Crewmeister's ETL and analytics capabilities. It provides a complete data pipeline from raw sensor data to interactive dashboard visualization, showcasing scalable data processing, SQL-based analytics, and business-focused visualizations.

## 🔄 Workflow Overview

### 1. **Data Simulation**
- **Source**: Raw sensor data generation (CSV or in-memory)
- **Format**: Industrial sensor readings (temperature, pressure, uptime)
- **Volume**: 100 rows of realistic propulsion test rig data
- **Frequency**: 6-minute intervals over 12 hours

### 2. **ETL Pipeline Processing**
- **Extract**: Read raw data from CSV files or generate simulated data
- **Transform**: Clean data, remove outliers, detect anomalies using Z-score analysis
- **Load**: Store processed data in SQLite database with optimized schema
- **Output**: Generate processed CSV with additional analytics columns

### 3. **Analytics & KPIs**
- **Key Performance Indicators**: Average temperature, alert count, uptime hours
- **Anomaly Detection**: Z-score analysis with configurable thresholds
- **Data Quality**: Null removal, range validation, outlier detection
- **Statistical Analysis**: Temperature and pressure trend analysis

### 4. **FastAPI Dashboard**
- **Real-time Visualization**: Chart.js integration for interactive graphs
- **API Endpoints**: RESTful API for data access and integration
- **Date Filtering**: Historical data analysis capabilities
- **CSV Export**: Data download functionality for external analysis

### 5. **Dependency-Free Demo**
- **Static HTML Generation**: Self-contained dashboard without external dependencies
- **Pre-processed Data**: Instant visualization using processed CSV files
- **Port Management**: Automatic port selection and browser opening
- **Zero Setup**: Requires only Python 3.8+ standard library

## 📁 File Structure

### **Core Pipeline Components**

#### `pipeline/etl_pipeline.py`
**Purpose**: Main ETL script for data processing pipeline
**Structure**:
```python
# Configuration and imports
# Environment variable loading
# Database connection setup

def extract_data():
    # Read CSV or generate simulated data
    # Return pandas DataFrame

def transform_data(df):
    # Data cleaning and validation
    # Anomaly detection (Z-score)
    # KPI calculation
    # Return processed DataFrame

def load_data(df):
    # SQLite database operations
    # Table creation and data insertion
    # CSV export for demo

def run_etl():
    # Orchestrate the complete pipeline
    # Error handling and logging
    # Return processing summary
```

#### `dashboard/app.py`
**Purpose**: FastAPI web application with API endpoints and dashboard
**Structure**:
```python
# FastAPI app initialization
# Database connection setup
# Jinja2 template configuration

# API Routes
@app.get("/api/kpis")
@app.get("/api/trends")
@app.get("/api/health")
@app.get("/dashboard")

# Helper Functions
def load_data()
def compute_kpis()
def prepare_trend_data()

# Error handling and logging
```

#### `demo/run_demo.py`
**Purpose**: Dependency-free demo script for instant visualization
**Structure**:
```python
# Standard library imports only
# Data loading from processed CSV
# Static HTML generation with embedded Chart.js
# HTTP server setup and browser opening
```

### **Data Files**

#### `data/simulated_raw.csv`
- **Content**: 100 rows of raw sensor data
- **Columns**: timestamp, temperature, pressure, uptime
- **Format**: CSV with realistic industrial values
- **Use**: Input for ETL pipeline processing

#### `data/simulated_processed.csv`
- **Content**: Processed data with analytics
- **Columns**: timestamp, temperature, pressure, uptime, z_score_temp, alert_status
- **Format**: CSV with additional statistical analysis
- **Use**: Input for dependency-free demo

#### `data/processed.db`
- **Content**: SQLite database with processed sensor data
- **Tables**: sensor_data (main table)
- **Schema**: Optimized for query performance
- **Use**: Primary data storage for FastAPI dashboard

### **Templates and Configuration**

#### `templates/dashboard.html`
- **Purpose**: HTML template for web dashboard
- **Features**: Chart.js integration, responsive design, interactive controls
- **Data Binding**: Jinja2 templating for server-side data injection
- **Functionality**: Date filtering, real-time updates, CSV export

#### `requirements.txt`
- **Content**: Python dependencies for full project
- **Core**: FastAPI, uvicorn, pandas, jinja2
- **Optional**: Development, testing, and monitoring packages
- **Note**: Demo requires only Python 3.8+ standard library

#### `env.example`
- **Purpose**: Environment variables template
- **Sections**: Data, dashboard, database, security, monitoring
- **Configuration**: 50+ settings for customization
- **Usage**: Copy to `.env` and modify as needed

### **Documentation and Testing**

#### `README.md`
- **Content**: Comprehensive project documentation
- **Sections**: Features, setup, API, maintenance
- **Audience**: Developers and end users
- **Format**: Professional markdown with examples

#### `tests/test_etl.py`
- **Purpose**: Unit and integration tests for ETL pipeline
- **Coverage**: Data extraction, transformation, loading
- **Mocking**: Database and file system isolation
- **Validation**: Edge cases and error conditions

#### `.github/workflows/ci.yml`
- **Purpose**: Continuous integration pipeline
- **Triggers**: Push to any branch
- **Actions**: Code linting, quality checks
- **Environment**: Ubuntu with Python 3.8

## 🔧 Code Block Structure

### **ETL Pipeline (`pipeline/etl_pipeline.py`)**

```python
# Configuration Section
import os, pandas, sqlite3, logging
from datetime import datetime
from dotenv import load_dotenv

# Environment setup
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Extract Function
def extract_data():
    """Load raw sensor data from CSV or generate simulated data"""
    # File existence check
    # CSV reading with error handling
    # Fallback to simulated data generation
    # Return pandas DataFrame

# Transform Function  
def transform_data(df):
    """Clean data and perform statistical analysis"""
    # Data validation and cleaning
    # Z-score calculation for anomaly detection
    # KPI computation
    # Alert status assignment
    # Return processed DataFrame

# Load Function
def load_data(df):
    """Store processed data in SQLite database"""
    # Database connection setup
    # Table creation with schema
    # Data insertion with error handling
    # CSV export for demo
    # Return processing summary

# Main Orchestration
def run_etl():
    """Execute complete ETL pipeline"""
    # Extract → Transform → Load workflow
    # Error handling and logging
    # Performance metrics
    # Return summary statistics
```

### **FastAPI Application (`dashboard/app.py`)**

```python
# Setup Section
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
import pandas, sqlite3, logging

# Application initialization
app = FastAPI(title="Smart Sensor Dashboard")
templates = Jinja2Templates(directory="templates")

# Data Loading Functions
def load_data(date_filter=None):
    """Load sensor data with optional date filtering"""
    # Database connection
    # SQL query construction
    # Date validation
    # Return pandas DataFrame

def compute_kpis(df):
    """Calculate key performance indicators"""
    # Statistical calculations
    # Alert counting
    # Range analysis
    # Return KPI dictionary

# API Endpoints
@app.get("/api/kpis")
async def get_kpis(date: str = None):
    """Return KPI data as JSON"""
    # Data loading
    # KPI computation
    # Response formatting

@app.get("/dashboard")
async def dashboard(request: Request, date: str = None):
    """Render dashboard HTML template"""
    # Data preparation
    # Template context
    # HTML response

# Error Handling
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
```

### **Demo Script (`demo/run_demo.py`)**

```python
# Standard Library Imports
import http.server, socketserver, csv, json, os
import webbrowser, socket

# Data Loading Section
def load_processed_data():
    """Load pre-processed CSV data"""
    # File existence check
    # CSV parsing
    # Data validation
    # Return structured data

# HTML Generation Section
def generate_dashboard_html(data):
    """Create static HTML dashboard"""
    # Chart.js CDN inclusion
    # CSS styling
    # JavaScript for interactivity
    # Data embedding
    # Return complete HTML

# Server Setup Section
def find_available_port():
    """Find available port for HTTP server"""
    # Port scanning
    # Conflict resolution
    # Return available port

def start_server(html_content, port):
    """Start HTTP server with dashboard"""
    # Server configuration
    # Request handling
    # Browser opening
    # Server startup

# Main Execution
if __name__ == "__main__":
    # Data loading
    # HTML generation
    # Server startup
    # User notification
```

## 🎯 Component Roles in Workflow

### **Data Flow**
1. **Raw Data** → `simulated_raw.csv` (industrial sensor readings)
2. **ETL Processing** → `etl_pipeline.py` (extract, transform, load)
3. **Processed Data** → `processed.db` + `simulated_processed.csv`
4. **Visualization** → `app.py` (FastAPI) or `run_demo.py` (static)
5. **User Interface** → `dashboard.html` (interactive dashboard)

### **Technology Stack**
- **Data Processing**: Pandas for ETL operations
- **Database**: SQLite for data storage
- **Web Framework**: FastAPI for API and dashboard
- **Visualization**: Chart.js for interactive graphs
- **Templating**: Jinja2 for HTML generation
- **Testing**: unittest for pipeline validation
- **CI/CD**: GitHub Actions for code quality

### **Scalability Considerations**
- **Modular Design**: Each component can be extended independently
- **Configuration**: Environment variables for customization
- **Error Handling**: Comprehensive logging and fallback mechanisms
- **Performance**: Optimized database queries and data structures
- **Deployment**: Docker support for containerized deployment

This architecture demonstrates modern data engineering practices while providing a practical solution for industrial sensor data monitoring and analysis. 