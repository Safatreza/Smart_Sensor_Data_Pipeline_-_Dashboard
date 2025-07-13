# Smart Sensor Data Pipeline & Dashboard

A comprehensive ETL pipeline and interactive dashboard system designed for industrial sensor data monitoring and analysis. This project provides scalable data processing, real-time visualization, and business-focused analytics for engineering operations with support for both SQLite and PostgreSQL/TimescaleDB backends.

## 📋 Table of Contents

- [🎯 Why This Matters](#-why-this-matters)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Full Setup](#️-full-setup)
- [🗄️ Database Configuration](#️-database-configuration)
- [🐳 Docker Deployment](#-docker-deployment)
- [📁 Project Structure](#-project-structure)
- [📸 Screenshots](#-screenshots)
- [🔧 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🔄 Maintenance](#-maintenance)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📞 Support](#-support)

## 🎯 Why This Matters

This solution aligns perfectly with **Crewmeister's** needs for:
- **Scalable ETL processes** for industrial data
- **SQL-based analytics** with real-time insights
- **Business-focused visualizations** for decision making
- **Production-ready architecture** for real-world sensor data
- **Flexible database backends** supporting both SQLite and PostgreSQL/TimescaleDB

## ✨ Features

### 🔄 **ETL Pipeline**
- **Modular data processing** with extraction, transformation, and loading stages
- **Anomaly detection** using Z-score analysis for temperature monitoring
- **Data quality checks** and outlier removal
- **Multi-database support** with SQLite and PostgreSQL/TimescaleDB
- **TimescaleDB hypertables** for time-series optimization
- **Configurable processing** via environment variables

### 📊 **FastAPI Dashboard**
- **Real-time data visualization** with Chart.js integration
- **Interactive KPI cards** showing average temperature, alert count, and uptime hours
- **Date filtering** for historical data analysis
- **RESTful API endpoints** for data access and integration
- **Responsive design** for desktop and mobile access
- **WebSocket support** for real-time updates

### 🗄️ **Database Support**
- **SQLite** (default) - Lightweight, file-based database
- **PostgreSQL** - Production-ready relational database
- **TimescaleDB** - Time-series optimized PostgreSQL extension
- **Automatic schema management** and indexing
- **Connection pooling** and optimized queries

### 🚀 **Dependency-Free Demo**
- **Zero-dependency demo script** requiring only Python 3.8+
- **Static HTML dashboard** with embedded Chart.js
- **Pre-processed data loading** for instant visualization
- **Port conflict handling** and automatic browser opening

### 📈 **Key Performance Indicators**
- **Average Temperature**: Real-time monitoring with range display
- **Alert Count**: Critical sensor alerts based on Z-score analysis
- **Uptime Hours**: Continuous operation tracking
- **Total Records**: Data collection statistics

### 🔍 **Anomaly Detection**
- **Z-score analysis** for statistical outlier detection
- **Configurable thresholds** for alert generation
- **Visual alert indicators** (red/green status)
- **Historical trend analysis**

## 🚀 Quick Start

Experience the dashboard instantly with our dependency-free demo:

```bash
# Navigate to the demo directory
cd demo

# Run the demo (requires only Python 3.8+)
python run_demo.py
```

The demo will:
- ✅ Load pre-processed sensor data
- ✅ Generate a static HTML dashboard
- ✅ Open your browser to `http://localhost:8000`
- ✅ Display interactive charts and KPIs

## 🛠️ Full Setup

### Prerequisites
- **Python 3.8** or higher
- **Git**
- **PostgreSQL** (optional, for production use)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-sensor-dashboard.git
   cd smart-sensor-dashboard
   ```

2. **Install dependencies**
   ```bash
   # For basic functionality
   pip install -r requirements_simple.txt
   
   # For full features
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy the environment template
   cp env.example .env
   
   # Edit .env file with your settings
   nano .env
   ```

4. **Run the ETL pipeline**
   ```bash
   python pipeline/etl_pipeline.py
   ```

5. **Launch the dashboard**
   ```bash
   # Option 1: Use the main application
   python main.py
   
   # Option 2: Use the dashboard app directly
   python dashboard/app.py
   ```

6. **Access the dashboard**
   - 🌐 **Dashboard**: `http://localhost:8000/dashboard`
   - 📚 **API Docs**: `http://localhost:8000/docs`
   - 🔍 **Health Check**: `http://localhost:8000/api/health`

## 🗄️ Database Configuration

The system supports multiple database backends configured via the `DATABASE_URL` environment variable:

### SQLite (Default)
```bash
# .env file
DATABASE_URL=sqlite:///data/processed.db
```
- **Pros**: No setup required, file-based, perfect for development
- **Cons**: Limited concurrency, not suitable for high-volume production

### PostgreSQL
```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/sensor_db
```
- **Pros**: Production-ready, excellent concurrency, ACID compliance
- **Cons**: Requires PostgreSQL installation and setup

### TimescaleDB (Recommended for Time-Series)
```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/sensor_db
```
- **Pros**: Optimized for time-series data, automatic partitioning, hypertables
- **Cons**: Requires TimescaleDB extension installation

### Setup PostgreSQL/TimescaleDB

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Install TimescaleDB** (optional)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install timescaledb-postgresql-14
   
   # macOS
   brew install timescaledb
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE sensor_db;
   CREATE USER sensor_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE sensor_db TO sensor_user;
   ```

4. **Enable TimescaleDB** (if using)
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

## 🐳 Docker Deployment

For containerized deployment:

```bash
# Build the Docker image
docker build -t sensor-dashboard .

# Run the container
docker run -p 8000:8000 sensor-dashboard

# Or use docker-compose
docker-compose up -d
```

## 📁 Project Structure

```
Smart_Sensor_Data_Pipeline_&_Dashboard/
├── 📁 pipeline/
│   ├── etl_pipeline.py          # ETL data processing pipeline
│   ├── db_utils.py              # Database abstraction layer
│   └── data_utils.py            # Shared data processing utilities
├── 📁 dashboard/
│   └── app.py                   # FastAPI web application
├── 📁 data/
│   ├── simulated_raw.csv        # Raw sensor data (100 rows)
│   └── simulated_processed.csv  # Processed data with analytics
├── 📁 demo/
│   └── run_demo.py             # Dependency-free demo script
├── 📁 templates/
│   └── dashboard.html          # HTML dashboard template
├── 📁 tests/
│   └── test_etl.py            # Unit and integration tests
├── 📁 .github/workflows/
│   └── ci.yml                 # CI/CD pipeline configuration
├── requirements.txt           # Full Python dependencies
├── requirements_simple.txt    # Minimal dependencies
├── env.example               # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### 📋 **pipeline/**
Contains the ETL pipeline and utilities:
- **`etl_pipeline.py`**: Main ETL processing pipeline
- **`db_utils.py`**: Database abstraction layer (SQLAlchemy)
- **`data_utils.py`**: Shared data processing functions
- **Data extraction** from CSV files
- **Transformation** with cleaning and anomaly detection
- **Loading** into configured database backend
- **KPI calculation** and metadata generation

### 📊 **dashboard/**
FastAPI web application with:
- **RESTful API endpoints** for data access
- **Interactive dashboard** with Chart.js
- **Real-time data visualization**
- **Date filtering** and trend analysis
- **WebSocket support** for live updates

### 📁 **data/**
Sample sensor data files:
- **Raw data** from industrial sensors
- **Processed data** with statistical analysis
- **Realistic values** for propulsion test rig

### 🎮 **demo/**
Dependency-free demonstration:
- **Static HTML dashboard** generation
- **Pre-processed data** loading
- **Zero external dependencies**
- **Instant visualization**

### 🎨 **templates/**
HTML templates for the web interface:
- **Responsive dashboard** design
- **Chart.js integration**
- **Interactive controls** and filters

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](screenshots/dashboard.png)
*Main dashboard showing KPI cards and temperature trends*

### Trend Analysis
![Trend Analysis](screenshots/trend_graph.png)
*Interactive temperature and pressure trend charts*

### API Documentation
![API Docs](screenshots/api_docs.png)
*Auto-generated FastAPI documentation*

*Note: Screenshots will be added as the project develops*

## 🔧 API Endpoints

### Core Endpoints
- `GET /dashboard` - Main dashboard interface
- `GET /api/kpis` - Key performance indicators
- `GET /api/trends` - Time series data for charts
- `GET /api/health` - System health check
- `GET /api/summary` - Comprehensive data summary
- `GET /api/download` - Download data as CSV
- `WS /ws/data` - WebSocket for real-time updates

### Query Parameters
- `date=YYYY-MM-DD` - Filter data by specific date

### Response Models
```json
{
  "avg_temp": 45.2,
  "avg_pressure": 1005.3,
  "alert_count": 3,
  "uptime_hours": 24,
  "total_records": 100,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pipeline --cov=dashboard

# Run specific test file
pytest tests/test_etl.py
```

## 🔄 Maintenance

### Updating Sensor Data
1. Replace `data/simulated_raw.csv` with new sensor data
2. Run the ETL pipeline: `python pipeline/etl_pipeline.py`
3. Restart the dashboard: `python main.py`

### Database Migration
1. Update `DATABASE_URL` in `.env` file
2. Run the ETL pipeline to create new schema
3. Verify data integrity with health check endpoint

### Performance Optimization
- **SQLite**: Suitable for development and small datasets
- **PostgreSQL**: Recommended for production with moderate data volume
- **TimescaleDB**: Best for high-volume time-series data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Use type hints for function parameters

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **SQLAlchemy** for database abstraction
- **Chart.js** for interactive visualizations
- **Pandas** for data processing capabilities

## 📞 Support

- **Documentation**: [USER_MANUAL.md](USER_MANUAL.md)
- **Issues**: [GitHub Issues](https://github.com/your-username/smart-sensor-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/smart-sensor-dashboard/discussions)

---

**Built with ❤️ for industrial data analytics** 