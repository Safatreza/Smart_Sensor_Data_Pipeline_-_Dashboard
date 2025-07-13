# Smart Sensor Data Dashboard - User Manual

A comprehensive guide to using the Smart Sensor Data Dashboard for monitoring, analyzing, and visualizing sensor data.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Interface](#dashboard-interface)
4. [Data Management](#data-management)
5. [API Usage](#api-usage)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Introduction

The Smart Sensor Data Dashboard is a powerful tool for processing and visualizing sensor data in real-time. It provides a complete solution for data extraction, transformation, loading (ETL), and visualization through an intuitive web interface.

### Key Features

- **Real-time Data Processing**: Automatically processes incoming sensor data
- **Interactive Visualizations**: Dynamic charts and graphs for data analysis
- **Sensor Monitoring**: Track sensor health, battery levels, and performance
- **Data Export**: Export data in various formats for further analysis
- **RESTful API**: Programmatic access to all dashboard features
- **Multi-sensor Support**: Monitor multiple sensors simultaneously

## Getting Started

### Prerequisites

Before using the dashboard, ensure you have:

- Python 3.8 or higher installed
- Required dependencies installed (see requirements.txt)
- Access to sensor data (CSV files, APIs, or databases)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/smart-sensor-data-dashboard.git
   cd smart-sensor-data-dashboard
   ```

2. **Install Dependencies**
   ```bash
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
   python dashboard/app.py
   ```

4. **Access Dashboard**
   Open your browser and navigate to `http://localhost:5000`

## Dashboard Interface

### Main Dashboard Layout

The dashboard is organized into several key sections:

#### 1. Navigation Bar
- **Dashboard Title**: Shows the current application name
- **Current Time**: Real-time clock display
- **Status Indicators**: System health and connection status

#### 2. Summary Metrics
Four key metric cards display:
- **Total Records**: Number of processed data records
- **Active Sensors**: Number of currently active sensors
- **Average Temperature**: Mean temperature across all sensors
- **Average Humidity**: Mean humidity across all sensors

#### 3. Real-time Charts
The main chart area shows:
- **Temperature Trends**: Line chart of temperature over time
- **Humidity Trends**: Line chart of humidity over time
- **Pressure Trends**: Line chart of atmospheric pressure
- **Interactive Controls**: Sensor filter and time range selector

#### 4. Sensor Status Panel
Right sidebar displays:
- **Sensor List**: All available sensors with status indicators
- **Battery Levels**: Visual battery status for each sensor
- **Signal Strength**: Connection quality indicators
- **Health Status**: Online/offline status

#### 5. Data Table
Bottom section shows:
- **Latest Readings**: Most recent sensor data
- **Sortable Columns**: Click headers to sort data
- **Search/Filter**: Find specific records quickly

### Chart Controls

#### Sensor Filter
- **Dropdown Menu**: Select specific sensors or "All Sensors"
- **Real-time Updates**: Charts update immediately when selection changes
- **Multi-sensor View**: Compare data across multiple sensors

#### Time Range
- **24 Hours**: Default view showing last 24 hours
- **Custom Range**: Select specific time periods
- **Real-time**: Live data updates every 30 seconds

#### Chart Types
- **Line Charts**: Show trends over time
- **Area Charts**: Highlight data ranges
- **Bar Charts**: Compare discrete values

### Interactive Features

#### Hover Information
- **Data Points**: Hover over chart points for detailed values
- **Tooltips**: Display timestamp, sensor ID, and measurement values
- **Context Menu**: Right-click for additional options

#### Zoom and Pan
- **Zoom In**: Click and drag to zoom into specific time periods
- **Zoom Out**: Double-click to reset zoom
- **Pan**: Click and drag to move around zoomed charts

#### Export Options
- **Chart Export**: Download charts as PNG, JPEG, or PDF
- **Data Export**: Export chart data as CSV or JSON
- **Print**: Print-friendly version of charts

## Data Management

### Data Sources

The dashboard supports multiple data sources:

#### CSV Files
```python
# Example CSV format
timestamp,sensor_id,temperature,humidity,pressure,battery_level,signal_strength
2023-01-01 12:00:00,SENSOR_001,22.5,65.2,1013.25,85.0,92.5
```

#### Database Connections
```python
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/sensor_db

# MySQL
DATABASE_URL=mysql://user:password@localhost/sensor_db

# SQLite (default)
DATABASE_URL=data/processed.db
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
   raw_data = etl.extract_raw_data("data/raw_sensors.csv")
   ```

2. **Transform**
   ```python
   # Clean and process data
   processed_data = etl.transform_data(raw_data)
   ```

3. **Load**
   ```python
   # Store in database
   etl.load_data(processed_data, "sensor_data")
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
- **Derived Metrics**: Temperature in Fahrenheit, humidity categories
- **Calculated Fields**: Moving averages, trends

### Data Retention

#### Storage Policies
- **Raw Data**: Stored in CSV files (configurable retention)
- **Processed Data**: Stored in SQLite database
- **Backup Strategy**: Automatic backups of processed data

#### Cleanup Procedures
```python
# Configure retention in .env
ETL_DATA_RETENTION_DAYS=90  # Keep data for 90 days
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
  "timestamp": "2023-01-01T12:00:00Z"
}
```

#### Latest Data
```bash
GET /api/latest-data?limit=100
```
**Parameters:**
- `limit`: Number of records to return (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2023-01-01T12:00:00Z",
      "sensor_id": "SENSOR_001",
      "temperature": 22.5,
      "humidity": 65.2,
      "pressure": 1013.25,
      "battery_level": 85.0,
      "signal_strength": 92.5
    }
  ]
}
```

#### Sensor Summary
```bash
GET /api/sensor-summary
```
**Response:**
```json
{
  "success": true,
  "data": {
    "total_records": 1500,
    "total_sensors": 10,
    "earliest_timestamp": "2023-01-01T00:00:00Z",
    "latest_timestamp": "2023-01-01T12:00:00Z",
    "sensor_stats": [
      {
        "sensor_id": "SENSOR_001",
        "record_count": 150,
        "avg_temperature": 22.5,
        "avg_humidity": 65.2,
        "avg_pressure": 1013.25,
        "avg_battery": 85.0,
        "avg_signal": 92.5
      }
    ]
  }
}
```

#### Time Series Data
```bash
GET /api/time-series?sensor_id=SENSOR_001&hours=24
```
**Parameters:**
- `sensor_id`: Specific sensor ID (optional)
- `hours`: Time range in hours (default: 24)

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamps": ["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"],
    "temperature": [22.5, 23.1],
    "humidity": [65.2, 64.8],
    "pressure": [1013.25, 1013.30],
    "battery_level": [85.0, 84.8],
    "signal_strength": [92.5, 92.3]
  }
}
```

#### Sensor List
```bash
GET /api/sensors
```
**Response:**
```json
{
  "success": true,
  "data": ["SENSOR_001", "SENSOR_002", "SENSOR_003"]
}
```

### API Authentication

For production use, implement authentication:

```python
# Add to dashboard/app.py
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/protected-endpoint')
@require_api_key
def protected_endpoint():
    return jsonify({'data': 'protected'})
```

### API Rate Limiting

Configure rate limiting in your environment:

```bash
# .env file
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=3600
```

## Advanced Features

### Custom Data Sources

#### Adding New Extractors

Extend the ETL pipeline to support new data sources:

```python
class CustomDataExtractor:
    def extract_from_mqtt(self, broker_url: str, topic: str) -> pd.DataFrame:
        """Extract data from MQTT broker."""
        import paho.mqtt.client as mqtt
        
        data = []
        def on_message(client, userdata, msg):
            data.append(json.loads(msg.payload))
        
        client = mqtt.Client()
        client.on_message = on_message
        client.connect(broker_url)
        client.subscribe(topic)
        client.loop_start()
        
        return pd.DataFrame(data)

    def extract_from_websocket(self, ws_url: str) -> pd.DataFrame:
        """Extract data from WebSocket."""
        import websocket
        
        data = []
        def on_message(ws, message):
            data.append(json.loads(message))
        
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        ws.run_forever()
        
        return pd.DataFrame(data)
```

#### Custom Transformations

Add custom data transformations:

```python
def custom_transform(self, df: pd.DataFrame) -> pd.DataFrame:
    """Apply custom transformations."""
    # Add rolling averages
    df['temp_rolling_avg'] = df['temperature'].rolling(window=10).mean()
    
    # Add seasonal decomposition
    from statsmodels.tsa.seasonal import seasonal_decompose
    decomposition = seasonal_decompose(df['temperature'], period=24)
    df['temp_trend'] = decomposition.trend
    df['temp_seasonal'] = decomposition.seasonal
    
    return df
```

### Machine Learning Integration

#### Anomaly Detection

Implement anomaly detection for sensor data:

```python
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
    
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in sensor data."""
        features = df[['temperature', 'humidity', 'pressure']].values
        anomalies = self.model.fit_predict(features)
        
        df['is_anomaly'] = anomalies == -1
        return df
```

#### Predictive Analytics

Add predictive capabilities:

```python
from sklearn.linear_model import LinearRegression

class PredictiveAnalytics:
    def __init__(self):
        self.model = LinearRegression()
    
    def predict_temperature(self, df: pd.DataFrame, hours_ahead: int = 24) -> pd.DataFrame:
        """Predict temperature for next N hours."""
        # Prepare features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Train model
        X = df[['hour', 'day_of_week', 'humidity', 'pressure']].dropna()
        y = df['temperature'].dropna()
        
        self.model.fit(X, y)
        
        # Make predictions
        future_features = self._create_future_features(hours_ahead)
        predictions = self.model.predict(future_features)
        
        return predictions
```

### Real-time Features

#### WebSocket Integration

Add real-time updates via WebSocket:

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('request_data')
def handle_data_request():
    # Send latest data to client
    data = get_latest_data()
    emit('sensor_update', data)

def broadcast_sensor_update(data):
    """Broadcast sensor updates to all connected clients."""
    socketio.emit('sensor_update', data)
```

#### Event-driven Processing

Implement event-driven data processing:

```python
import asyncio
from datetime import datetime

class EventProcessor:
    def __init__(self):
        self.subscribers = []
    
    def subscribe(self, callback):
        """Subscribe to sensor events."""
        self.subscribers.append(callback)
    
    async def process_event(self, event_data):
        """Process incoming sensor events."""
        # Process the event
        processed_data = await self.transform_event(event_data)
        
        # Notify subscribers
        for callback in self.subscribers:
            await callback(processed_data)
    
    async def transform_event(self, event_data):
        """Transform raw event data."""
        # Add timestamp if not present
        if 'timestamp' not in event_data:
            event_data['timestamp'] = datetime.now().isoformat()
        
        # Validate data
        if not self.validate_event(event_data):
            raise ValueError("Invalid event data")
        
        return event_data
```

## Troubleshooting

### Common Issues

#### Dashboard Won't Start

**Problem**: Dashboard fails to start with error messages.

**Solutions**:
1. **Check Dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Verify Port Availability**
   ```bash
   # Check if port 5000 is in use
   netstat -an | grep 5000
   
   # Use different port
   export DASHBOARD_PORT=5001
   ```

3. **Check Database**
   ```bash
   # Ensure data directory exists
   mkdir -p data
   
   # Check database file
   ls -la data/processed.db
   ```

#### No Data Displayed

**Problem**: Dashboard loads but shows no data.

**Solutions**:
1. **Check Data Files**
   ```bash
   # Verify data files exist
   ls -la data/*.csv
   ls -la data/*.db
   ```

2. **Run ETL Pipeline**
   ```bash
   python pipeline/etl_pipeline.py
   ```

3. **Check Database Content**
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

**Solutions**:
1. **Check Auto-refresh Settings**
   - Verify `DASHBOARD_REFRESH_INTERVAL` in .env
   - Check browser console for JavaScript errors

2. **Manual Refresh**
   - Click refresh buttons in dashboard
   - Use browser refresh (F5)

3. **Check API Endpoints**
   ```bash
   curl http://localhost:5000/api/health
   curl http://localhost:5000/api/latest-data
   ```

#### Performance Issues

**Problem**: Dashboard is slow or unresponsive.

**Solutions**:
1. **Optimize Database**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_timestamp ON sensor_data (timestamp);
   CREATE INDEX idx_sensor_id ON sensor_data (sensor_id);
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
python dashboard/app.py
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
   def validate_sensor_data(data):
       """Validate sensor data before processing."""
       required_fields = ['timestamp', 'sensor_id', 'temperature']
       for field in required_fields:
           if field not in data:
               raise ValueError(f"Missing required field: {field}")
       
       # Check value ranges
       if not (0 <= data['temperature'] <= 100):
           raise ValueError("Temperature out of range")
   ```

3. **Error Handling**
   ```python
   try:
       processed_data = etl.run_pipeline(input_file)
   except FileNotFoundError:
       logger.error("Input file not found")
       # Handle gracefully
   except Exception as e:
       logger.error(f"ETL pipeline failed: {e}")
       # Send alert
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Use appropriate data types
   CREATE TABLE sensor_data (
       id INTEGER PRIMARY KEY,
       timestamp DATETIME NOT NULL,
       sensor_id TEXT NOT NULL,
       temperature REAL,
       humidity REAL,
       pressure REAL
   );
   
   -- Add composite indexes
   CREATE INDEX idx_sensor_time ON sensor_data (sensor_id, timestamp);
   ```

2. **Caching Strategy**
   ```python
   # Cache frequently accessed data
   @cache.memoize(timeout=300)
   def get_sensor_summary():
       return calculate_summary()
   
   # Cache API responses
   @cache.cached(timeout=60)
   def get_latest_data():
       return fetch_latest_data()
   ```

3. **Batch Processing**
   ```python
   def process_batch(data_batch, batch_size=1000):
       """Process data in batches for better performance."""
       for i in range(0, len(data_batch), batch_size):
           batch = data_batch[i:i + batch_size]
           process_single_batch(batch)
   ```

### Security

1. **Input Validation**
   ```python
   from marshmallow import Schema, fields, validate
   
   class SensorDataSchema(Schema):
       sensor_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
       temperature = fields.Float(validate=validate.Range(min=-50, max=100))
       humidity = fields.Float(validate=validate.Range(min=0, max=100))
   ```

2. **API Security**
   ```python
   # Rate limiting
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/api/data')
   @limiter.limit("100 per minute")
   def get_data():
       return jsonify(data)
   ```

3. **Environment Security**
   ```bash
   # Use environment variables for secrets
   export SECRET_KEY=$(openssl rand -hex 32)
   export DATABASE_PASSWORD=$(openssl rand -base64 32)
   ```

### Monitoring

1. **Health Checks**
   ```python
   @app.route('/health')
   def health_check():
       return jsonify({
           'status': 'healthy',
           'timestamp': datetime.now().isoformat(),
           'version': '1.0.0'
       })
   ```

2. **Metrics Collection**
   ```python
   from prometheus_client import Counter, Histogram
   
   # Define metrics
   requests_total = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
   
   # Track metrics
   @app.before_request
   def before_request():
       requests_total.inc()
   
   @app.after_request
   def after_request(response):
       request_duration.observe(time.time() - start_time)
       return response
   ```

3. **Logging**
   ```python
   import logging
   from logging.handlers import RotatingFileHandler
   
   # Configure logging
   handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=3)
   handler.setFormatter(logging.Formatter(
       '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
   ))
   app.logger.addHandler(handler)
   app.logger.setLevel(logging.INFO)
   ```

---

This user manual provides comprehensive guidance for using the Smart Sensor Data Dashboard. For additional support, please refer to the project documentation or contact the development team. 