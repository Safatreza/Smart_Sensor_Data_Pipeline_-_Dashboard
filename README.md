# Smart Sensor Data Pipeline & Dashboard

A comprehensive ETL pipeline and interactive dashboard system designed for industrial sensor data monitoring and analysis. This project provides scalable data processing, real-time visualization, and business-focused analytics for engineering operations.

## 📋 Table of Contents

- [🎯 Why This Matters](#-why-this-matters)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Full Setup](#️-full-setup)
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

## ✨ Features

### 🔄 **ETL Pipeline**
- **Modular data processing** with extraction, transformation, and loading stages
- **Anomaly detection** using Z-score analysis for temperature monitoring
- **Data quality checks** and outlier removal
- **SQLite database storage** with optimized schema
- **Configurable processing** via environment variables

### 📊 **FastAPI Dashboard**
- **Real-time data visualization** with Chart.js integration
- **Interactive KPI cards** showing average temperature, alert count, and uptime hours
- **Date filtering** for historical data analysis
- **RESTful API endpoints** for data access and integration
- **Responsive design** for desktop and mobile access

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

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-sensor-dashboard.git
   cd smart-sensor-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy the environment template
   cp env.example .env
   
   # Edit .env file with your settings (optional)
   nano .env
   ```

4. **Run the ETL pipeline**
   ```bash
   python pipeline/etl_pipeline.py
   ```

5. **Launch the dashboard**
   ```bash
   python dashboard/app.py
   ```

6. **Access the dashboard**
   - 🌐 **Dashboard**: `http://localhost:8000/dashboard`
   - 📚 **API Docs**: `http://localhost:8000/docs`
   - 🔍 **Health Check**: `http://localhost:8000/api/health`

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
│   └── etl_pipeline.py          # ETL data processing pipeline
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
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### 📋 **pipeline/**
Contains the ETL pipeline for data processing:
- **Data extraction** from CSV files
- **Transformation** with cleaning and anomaly detection
- **Loading** into SQLite database
- **KPI calculation** and metadata generation

### 📊 **dashboard/**
FastAPI web application with:
- **RESTful API endpoints** for data access
- **Interactive dashboard** with Chart.js
- **Real-time data visualization**
- **Date filtering** and trend analysis

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

### Query Parameters
- `date=YYYY-MM-DD` - Filter data by specific date
- `download=csv` - Download data as CSV file

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
3. Restart the dashboard: `python dashboard/app.py`

### Extending the Pipeline
1. Add new transformation functions in `pipeline/etl_pipeline.py`
2. Update the database schema if needed
3. Add corresponding API endpoints in `dashboard/app.py`
4. Update the dashboard template in `templates/dashboard.html`

### Configuration Updates
- Modify `.env` file for environment-specific settings
- Update `requirements.txt` for new dependencies
- Adjust anomaly detection thresholds in the ETL pipeline

## 🤝 Contributing

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Chart.js** for interactive data visualization
- **FastAPI** for modern web API development
- **Pandas** for data processing and analysis
- **SQLite** for lightweight database storage

## 📞 Support

For questions, issues, or contributions:
- 🐛 Create an issue on GitHub
- 📧 Contact the development team
- 📖 Check the documentation in the `docs/` folder

---

**Built with ❤️ for industrial sensor data monitoring and analysis** 