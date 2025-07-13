# Smart Sensor Data Dashboard - Simplified Version

A complete FastAPI application that demonstrates a smart sensor data pipeline and dashboard. This version is designed to be run easily with minimal setup.

## Features

- 🚀 **Easy Setup**: Single file application with minimal dependencies
- 📊 **Interactive Dashboard**: Real-time charts and KPIs
- 🔄 **REST API**: Complete API endpoints for data access
- ⚡ **WebSocket**: Real-time data streaming
- 📱 **Responsive Design**: Works on desktop and mobile
- 💾 **SQLite Database**: Built-in data storage with sample data
- 📈 **Data Visualization**: Temperature and pressure trend charts

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_simple.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Open Dashboard

Open your browser and go to: **http://localhost:8000**

## What You'll See

- **Dashboard**: Interactive charts and KPIs at http://localhost:8000
- **API Documentation**: Auto-generated docs at http://localhost:8000/docs
- **Health Check**: System status at http://localhost:8000/api/health

## API Endpoints

- `GET /` - Redirects to dashboard
- `GET /dashboard` - Main dashboard page
- `GET /api/kpis` - Get Key Performance Indicators
- `GET /api/trends` - Get trend data for charts
- `GET /api/health` - System health check
- `GET /api/download` - Download data as CSV
- `WS /ws/data` - WebSocket for real-time data

## Sample Data

The application automatically generates 100 sample sensor readings over the last 24 hours, including:
- Temperature readings (20-100°C)
- Pressure readings (900-1100 kPa)
- Uptime values (1-100 hours)
- Alert levels based on thresholds

## Customization

You can easily modify the application by editing `main.py`:

- **Data Generation**: Modify the `init_database()` function
- **Dashboard Design**: Update the `DASHBOARD_HTML` template
- **API Endpoints**: Add new routes to the FastAPI app
- **Charts**: Customize Chart.js configurations

## Troubleshooting

### Port Already in Use
If port 8000 is busy, modify the port in the `main()` function:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, ...)
```

### Database Issues
The application creates a `sensor_data.db` file automatically. If you encounter issues, delete this file and restart the application.

### Dependencies
Make sure you have Python 3.8+ and install all requirements:
```bash
pip install fastapi uvicorn pandas pydantic jinja2
```

## Next Steps

This simplified version demonstrates the core functionality. For production use, consider:

- Adding authentication
- Implementing real sensor data sources
- Adding more sophisticated data processing
- Setting up proper logging and monitoring
- Deploying to a production server

## Support

If you encounter any issues, check the console output for error messages. The application includes comprehensive logging to help diagnose problems. 