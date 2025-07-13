# Smart Sensor Data Dashboard - User Manual

A comprehensive guide to using the Smart Sensor Data Dashboard for monitoring, analyzing, and visualizing sensor data with support for SQLite and PostgreSQL/TimescaleDB backends.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Database Configuration](#database-configuration)
4. [Dashboard Interface](#dashboard-interface)
5. [Data Management](#data-management)
6. [API Usage](#api-usage)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Introduction

The Smart Sensor Data Dashboard is a powerful tool for processing and visualizing sensor data in real-time. It provides a complete solution for data extraction, transformation, loading (ETL), and visualization through an intuitive web interface with flexible database backend support.

### Key Features

- **Real-time Data Processing**: Automatically processes incoming sensor data
- **Interactive Visualizations**: Dynamic charts and graphs for data analysis
- **Multi-Database Support**: SQLite, PostgreSQL, and TimescaleDB backends
- **Sensor Monitoring**: Track sensor health, battery levels, and performance
- **Data Export**: Export data in various formats for further analysis
- **RESTful API**: Programmatic access to all dashboard features
- **WebSocket Support**: Real-time data streaming
- **Multi-sensor Support**: Monitor multiple sensors simultaneously

## Getting Started

### Prerequisites

Before using the dashboard, ensure you have:

- Python 3.8 or higher installed
- Required dependencies installed (see requirements.txt)
- Access to sensor data (CSV files, APIs, or databases)
- PostgreSQL (optional, for production use)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/smart-sensor-data-dashboard.git
   cd smart-sensor-data-dashboard
   ```

2. **Install Dependencies**
   ```bash
   # For basic functionality
   pip install -r requirements_simple.txt
   
   # For full features
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the Demo**
   ```bash
   python demo/run_demo.py
   ```

### First Run

1. **Generate Sample Data** (if needed)
   ```bash
   python -c "from pipeline.etl_pipeline import generate_simulated_data; generate_simulated_data()"
   ```

2. **Process Data**
   ```bash
   python pipeline/etl_pipeline.py
   ```

3. **Start Dashboard**
   ```bash
   # Option 1: Use the main application
   python main.py
   
   # Option 2: Use the dashboard app directly
   python dashboard/app.py
   ```

4. **Access Dashboard**
   Open your browser and navigate to `http://localhost:8000`

## Database Configuration

The dashboard supports multiple database backends configured via the `DATABASE_URL` environment variable in your `.env` file.

### SQLite (Default)

**Configuration:**
```bash
DATABASE_URL=sqlite:///data/processed.db
```

**Pros:**
- No setup required
- File-based storage
- Perfect for development and testing
- Zero configuration

**Cons:**
- Limited concurrency
- Not suitable for high-volume production
- No network access

**Best for:** Development, testing, small datasets

### PostgreSQL

**Configuration:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sensor_db
```

**Pros:**
- Production-ready
- Excellent concurrency
- ACID compliance
- Network accessible
- Advanced features

**Cons:**
- Requires PostgreSQL installation
- More complex setup
- Resource intensive

**Best for:** Production environments, moderate data volume

### TimescaleDB (Recommended for Time-Series)

**Configuration:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sensor_db
```

**Pros:**
- Optimized for time-series data
- Automatic partitioning
- Hypertables for performance
- All PostgreSQL features
- Built-in time-series functions

**Cons:**
- Requires TimescaleDB extension
- More complex setup than SQLite

**Best for:** High-volume time-series data, production environments

### Setup PostgreSQL/TimescaleDB

#### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

**Windows:**
Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

#### 2. Install TimescaleDB (Optional)

**Ubuntu/Debian:**
```bash
sudo apt-get install timescaledb-postgresql-14
```

**macOS:**
```bash
brew install timescaledb
```

#### 3. Create Database and User

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database
CREATE DATABASE sensor_db;

-- Create user
CREATE USER sensor_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sensor_db TO sensor_user;

-- Connect to the new database
\c sensor_db

-- Enable TimescaleDB extension (if using TimescaleDB)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Exit
\q
```

#### 4. Update Environment Configuration

```bash
# .env file
DATABASE_URL=postgresql://sensor_user:your_secure_password@localhost:5432/sensor_db
```

### Database Migration

To switch between database backends:

1. **Update Configuration**
   ```bash
   # Edit .env file
   nano .env
   # Change DATABASE_URL to new backend
   ```

2. **Run ETL Pipeline**
   ```bash
   python pipeline/etl_pipeline.py
   ```

3. **Verify Migration**
   ```bash
   # Check health endpoint
   curl http://localhost:8000/api/health
   ```

## Dashboard Interface

### Main Dashboard Layout

The dashboard is organized into several key sections:

#### 1. Navigation Bar
- **Dashboard Title**: Shows the current application name
- **Current Time**: Real-time clock display
- **Status Indicators**: System health and connection status

#### 2. Summary Metrics
Four key metric cards display:
- **Average Temperature**: Mean temperature across all sensors
- **Average Pressure**: Mean pressure across all sensors
- **Alert Count**: Number of critical alerts
- **Uptime Hours**: Total system uptime

#### 3. Real-time Charts
The main chart area shows:
- **Temperature Trends**: Line chart of temperature over time
- **Pressure Trends**: Line chart of pressure over time
- **Interactive Controls**: Date filter and refresh buttons

#### 4. Data Controls
Bottom section includes:
- **Date Filter**: Select specific date ranges
- **Refresh Button**: Manual data refresh
- **Download CSV**: Export data functionality

### Chart Controls

#### Date Filter
- **Date Picker**: Select specific dates for analysis
- **Real-time Updates**: Charts update immediately when selection changes
- **Historical Analysis**: View data from any date range

#### Time Range
- **All Data**: Default view showing all available data
- **Custom Range**: Select specific time periods
- **Real-time**: Live data updates every 30 seconds

#### Chart Types
- **Line Charts**: Show trends over time
- **Interactive Hover**: Detailed information on data points
- **Responsive Design**: Adapts to screen size

### Interactive Features

#### Hover Information
- **Data Points**: Hover over chart points for detailed values
- **Tooltips**: Display timestamp and measurement values
- **Context Menu**: Right-click for additional options

#### Export Options
- **CSV Download**: Export filtered data as CSV
- **API Access**: Programmatic data access
- **Real-time Streaming**: WebSocket connection for live updates

## Data Management

### Data Sources

The dashboard supports multiple data sources:

#### CSV Files
```python
# Example CSV format
timestamp,temperature,pressure,uptime
2023-01-01 12:00:00,22.5,1013.25,24
```

#### Database Connections
```python
# PostgreSQL/TimescaleDB
DATABASE_URL=postgresql://user:password@localhost/sensor_db

# SQLite (default)
DATABASE_URL=sqlite:///data/processed.db
```

#### REST APIs
```python
# Configure API endpoints in .env
SENSOR_API_URL=https://api.example.com/sensors
API_KEY=your-api-key
```

### Data Processing

#### ETL Pipeline

The ETL (Extract, Transform, Load) pipeline processes data in three stages:

1. **Extract**
   ```python
   # Extract data from source
   raw_data = etl.extract_data("data/raw_sensors.csv")
   ```

2. **Transform**
   ```python
   # Clean and process data
   processed_data, kpis = etl.transform_data(raw_data)
   ```

3. **Load**
   ```python
   # Store in configured database
   etl.load_data(processed_data)
   ```

#### Data Cleaning

The system automatically:
- **Removes Outliers**: Uses IQR method to detect and handle outliers
- **Fills Missing Values**: Replaces NaN values with median
- **Validates Data**: Checks for reasonable value ranges
- **Converts Units**: Automatically converts temperature units

#### Data Enrichment

Additional features are added:
- **Time Features**: Hour, day of week, month
- **Derived Metrics**: Temperature ranges, pressure categories
- **Calculated Fields**: Moving averages, trends

### Data Retention

#### Storage Policies
- **Raw Data**: Stored in CSV files (configurable retention)
- **Processed Data**: Stored in configured database backend
- **Backup Strategy**: Automatic backups of processed data

#### Cleanup Procedures
```python
# Configure retention in .env
DATA_RETENTION_DAYS=90  # Keep data for 90 days
```

## API Usage

### REST API Endpoints

The dashboard provides a complete REST API for programmatic access:

#### Health Check
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "record_count": 1500,
  "timestamp": "2023-01-01T12:00:00Z",
  "version": "2.0.0"
}
```

#### Key Performance Indicators
```bash
GET /api/kpis?date=2023-01-01
```
**Parameters:**
- `date`: Optional date filter (YYYY-MM-DD format)

**Response:**
```json
{
  "avg_temp": 45.2,
  "avg_pressure": 1005.3,
  "alert_count": 3,
  "uptime_hours": 24,
  "total_records": 100,
  "date_filter": "2023-01-01",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

#### Trend Data
```bash
GET /api/trends?date=2023-01-01
```
**Response:**
```json
{
  "timestamps": ["2023-01-01 12:00:00", "2023-01-01 12:15:00"],
  "temperatures": [22.5, 23.1],
  "pressures": [1013.25, 1013.30],
  "uptime_hours": [24, 24],
  "date_filter": "2023-01-01",
  "record_count": 2
}
```

#### Data Download
```bash
GET /api/download?date=2023-01-01
```
**Response:** CSV file download

#### WebSocket Real-time Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/data');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

### API Authentication

Currently, the API is open for development. For production use:

1. **Add Authentication Middleware**
2. **Configure API Keys**
3. **Implement Rate Limiting**

## Advanced Features

### TimescaleDB Hypertables

When using TimescaleDB, the system automatically creates hypertables for optimal time-series performance:

```sql
-- Automatic hypertable creation
SELECT create_hypertable('sensor_data', 'timestamp');

-- Time-series queries
SELECT time_bucket('1 hour', timestamp) as hour,
       avg(temperature) as avg_temp
FROM sensor_data
WHERE timestamp > now() - interval '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Performance Optimization

#### Database-Specific Optimizations

**SQLite:**
- File-based storage
- Suitable for development
- Limited concurrency

**PostgreSQL:**
- Connection pooling
- Index optimization
- Query optimization

**TimescaleDB:**
- Automatic partitioning
- Time-series functions
- Compression

#### Caching Strategies

```python
# Configure caching in .env
CACHE_TTL=300  # 5 minutes
REDIS_URL=redis://localhost:6379
```

### Monitoring and Alerts

#### Health Monitoring
```bash
# Health check endpoint
curl http://localhost:8000/api/health

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "record_count": 1500
}
```

#### Alert Configuration
```python
# Configure in .env
TEMPERATURE_THRESHOLD_HIGH=80.0
PRESSURE_THRESHOLD_HIGH=1100.0
Z_SCORE_THRESHOLD_TEMPERATURE=2.0
Z_SCORE_THRESHOLD_PRESSURE=2.5
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

**Problem**: Cannot connect to database.

**Solutions:**
1. **Check DATABASE_URL**
   ```bash
   # Verify .env file
   cat .env | grep DATABASE_URL
   ```

2. **Test PostgreSQL Connection**
   ```bash
   # Test connection
   psql postgresql://user:password@localhost:5432/sensor_db
   ```

3. **Check Database Status**
   ```bash
   # PostgreSQL
   sudo systemctl status postgresql
   
   # SQLite
   ls -la data/processed.db
   ```

#### Data Loading Issues

**Problem**: No data appears in dashboard.

**Solutions:**
1. **Run ETL Pipeline**
   ```bash
   python pipeline/etl_pipeline.py
   ```

2. **Check Data Files**
   ```bash
   ls -la data/
   head -5 data/simulated_raw.csv
   ```

3. **Verify Database Content**
   ```python
   import sqlite3
   conn = sqlite3.connect('data/processed.db')
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM sensor_data")
   print(f"Records: {cursor.fetchone()[0]}")
   conn.close()
   ```

#### Charts Not Updating

**Problem**: Charts remain static and don't refresh.

**Solutions:**
1. **Check Auto-refresh Settings**
   - Verify `DASHBOARD_REFRESH_INTERVAL` in .env
   - Check browser console for JavaScript errors

2. **Manual Refresh**
   - Click refresh buttons in dashboard
   - Use browser refresh (F5)

3. **Check API Endpoints**
   ```bash
   curl http://localhost:8000/api/health
   curl http://localhost:8000/api/kpis
   ```

#### Performance Issues

**Problem**: Dashboard is slow or unresponsive.

**Solutions:**
1. **Optimize Database**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_timestamp ON sensor_data (timestamp);
   CREATE INDEX idx_temperature ON sensor_data (temperature);
   ```

2. **Reduce Data Volume**
   ```python
   # Limit data in queries
   LIMIT = 1000  # Reduce from default
   ```

3. **Enable Caching**
   ```python
   # Add Redis caching
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
python main.py
```

### Log Files

Check log files for detailed error information:

```bash
# View application logs
tail -f logs/dashboard.log

# Check system logs
journalctl -u smart-sensor-dashboard -f
```

## Best Practices

### Data Management

1. **Regular Backups**
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   cp data/processed.db data/backup_$DATE.db
   ```

2. **Data Validation**
   ```python
   # Validate data before processing
   def validate_sensor_data(data):
       assert data['temperature'].between(-50, 150)
       assert data['pressure'].between(800, 1200)
   ```

3. **Performance Monitoring**
   ```python
   # Monitor query performance
   import time
   start_time = time.time()
   # ... database query ...
   print(f"Query took {time.time() - start_time:.2f} seconds")
   ```

### Security

1. **Environment Variables**
   ```bash
   # Never commit sensitive data
   echo ".env" >> .gitignore
   ```

2. **Database Security**
   ```sql
   -- Use strong passwords
   ALTER USER sensor_user PASSWORD 'strong_password_here';
   
   -- Limit connections
   ALTER USER sensor_user CONNECTION LIMIT 10;
   ```

3. **API Security**
   ```python
   # Add authentication
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBearer
   ```

### Performance

1. **Database Optimization**
   ```sql
   -- Regular maintenance
   VACUUM ANALYZE sensor_data;
   
   -- Monitor slow queries
   SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;
   ```

2. **Caching Strategy**
   ```python
   # Cache frequently accessed data
   @cache.memoize(timeout=300)
   def get_kpis(date=None):
       # ... KPI calculation ...
   ```

3. **Resource Management**
   ```python
   # Use connection pooling
   engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30)
   ```

---

**For additional support, see the main README.md file or create an issue on GitHub.** 