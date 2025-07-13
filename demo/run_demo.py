#!/usr/bin/env python3
"""
Dependency-Free Sensor Data Dashboard Demo

A standalone demo script that creates and serves a sensor data dashboard
using only Python's standard library. No external dependencies required.

Author: Smart Sensor Data Dashboard Team
Version: 2.0.0
"""

import http.server
import socketserver
import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import webbrowser
import time
import threading


def load_demo_data(csv_path: str = "../data/simulated_processed.csv") -> Tuple[List[Dict], Dict]:
    """
    Load pre-processed sensor data from CSV file and compute KPIs.
    
    Args:
        csv_path: Path to the processed CSV file
        
    Returns:
        Tuple of (data_list, kpis_dict)
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV file is malformed
    """
    print(f"Loading demo data from {csv_path}...")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        error_msg = f"Demo data file not found: {csv_path}"
        print(f"❌ ERROR: {error_msg}")
        print(f"💡 Please ensure the ETL pipeline has been run to generate the processed data.")
        print(f"📁 Expected location: {os.path.abspath(csv_path)}")
        raise FileNotFoundError(error_msg)
    
    data = []
    total_temp = 0.0
    alert_count = 0
    max_uptime = 0
    row_count = 0
    error_count = 0
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Skip comment lines (lines starting with #)
            lines = csvfile.readlines()
            data_lines = [line for line in lines if not line.strip().startswith('#')]
            
            if not data_lines:
                raise ValueError("No data lines found in CSV file (only comments)")
            
            # Create a StringIO object for csv.DictReader
            from io import StringIO
            csv_content = StringIO(''.join(data_lines))
            reader = csv.DictReader(csv_content)
            
            # Validate required columns
            required_columns = ['timestamp', 'temperature', 'pressure', 'uptime']
            if reader.fieldnames is None:
                raise ValueError("CSV file has no headers")
            if not all(col in reader.fieldnames for col in required_columns):
                missing_cols = [col for col in required_columns if col not in reader.fieldnames]
                raise ValueError(f"CSV missing required columns: {missing_cols}. Found: {reader.fieldnames}")
            
            for row in reader:
                # Convert numeric values
                try:
                    row['temperature'] = float(row['temperature'])
                    row['pressure'] = float(row['pressure'])
                    row['uptime'] = float(row['uptime'])  # Allow float values for uptime
                    
                    # Parse timestamp
                    if 'timestamp' in row and row['timestamp']:
                        # Handle different timestamp formats
                        timestamp_str = row['timestamp']
                        try:
                            # Try parsing as ISO format
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            try:
                                # Try parsing as standard format
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # Use current time if parsing fails
                                timestamp = datetime.now()
                        
                        row['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Check for alerts (if alert columns exist)
                    if 'temperature_alert' in row and row['temperature_alert'] == 'red':
                        alert_count += 1
                    elif 'pressure_alert' in row and row['pressure_alert'] == 'red':
                        alert_count += 1
                    
                    # Update KPIs
                    total_temp += row['temperature']
                    max_uptime = max(max_uptime, row['uptime'])
                    
                    data.append(row)
                    row_count += 1
                    
                except (ValueError, KeyError) as e:
                    error_count += 1
                    print(f"⚠️  Warning: Skipping malformed row {row_count + error_count}: {e}")
                    continue
            
            if row_count == 0:
                raise ValueError("No valid data rows found in CSV file")
            
            print(f"✅ Successfully loaded {row_count} data records")
            if error_count > 0:
                print(f"⚠️  Skipped {error_count} malformed rows")
    
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    # Compute KPIs
    avg_temp = total_temp / len(data) if data else 0.0
    
    kpis = {
        'avg_temp': round(avg_temp, 2),
        'alert_count': alert_count,
        'uptime_hours': max_uptime,
        'total_records': len(data),
        'data_quality': f"{len(data)}/{row_count + error_count}" if error_count > 0 else f"{len(data)} records"
    }
    
    print(f"📊 KPIs computed: avg_temp={kpis['avg_temp']}°C, "
          f"alerts={kpis['alert_count']}, uptime={kpis['uptime_hours']}h")
    
    return data, kpis


def generate_html(data: List[Dict], kpis: Dict, output_path: str = "demo_dashboard.html") -> str:
    """
    Generate a static HTML dashboard with embedded Chart.js.
    
    Args:
        data: List of sensor data dictionaries
        kpis: Dictionary of computed KPIs
        output_path: Path to save the HTML file
        
    Returns:
        Path to the generated HTML file
    """
    print(f"Generating HTML dashboard at {output_path}...")
    
    # Prepare chart data
    timestamps = []
    temperatures = []
    pressures = []
    
    for row in data:
        timestamps.append(row.get('timestamp', ''))
        temperatures.append(row.get('temperature', 0))
        pressures.append(row.get('pressure', 0))
    
    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Data Dashboard Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .kpi-section {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .kpi-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .kpi-label {{
            font-size: 1.1em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .alert-card {{
            border-color: #dc3545;
        }}
        
        .alert-card .kpi-value {{
            color: #dc3545;
        }}
        
        .chart-section {{
            padding: 30px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-online {{
            background-color: #28a745;
        }}
        
        .status-warning {{
            background-color: #ffc107;
        }}
        
        .status-offline {{
            background-color: #dc3545;
        }}
        
        @media (max-width: 768px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sensor Data Dashboard</h1>
            <p>Real-time monitoring of industrial sensor data</p>
        </div>
        
        <div class="kpi-section">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['avg_temp']}°C</div>
                    <div class="kpi-label">Average Temperature</div>
                </div>
                
                <div class="kpi-card {'alert-card' if kpis['alert_count'] > 0 else ''}">
                    <div class="kpi-value">{kpis['alert_count']}</div>
                    <div class="kpi-label">Active Alerts</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['uptime_hours']}h</div>
                    <div class="kpi-label">System Uptime</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['total_records']}</div>
                    <div class="kpi-label">Data Points</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <span class="status-indicator status-online"></span>
                <strong>System Status:</strong> Online
                <span style="margin-left: 20px;">
                    <strong>Data Quality:</strong> {kpis['data_quality']}
                </span>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-container">
                <div class="chart-title">Temperature Trends Over Time</div>
                <canvas id="temperatureChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container" style="margin-top: 30px;">
                <div class="chart-title">Pressure Trends Over Time</div>
                <canvas id="pressureChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="footer">
            <p>🛠️ Built with Python Standard Library | 📊 Chart.js Visualization | 🚀 Real-time Data</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // Temperature Chart
        const tempCtx = document.getElementById('temperatureChart').getContext('2d');
        const tempChart = new Chart(tempCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timestamps)},
                datasets: [{{
                    label: 'Temperature (°C)',
                    data: {json.dumps(temperatures)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }}
                }},
                scales: {{
                    x: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Time'
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.1)'
                        }}
                    }},
                    y: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Temperature (°C)'
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.1)'
                        }},
                        beginAtZero: false
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }}
            }}
        }});

        // Pressure Chart
        const pressureCtx = document.getElementById('pressureChart').getContext('2d');
        const pressureChart = new Chart(pressureCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timestamps)},
                datasets: [{{
                    label: 'Pressure (hPa)',
                    data: {json.dumps(pressures)},
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#28a745',
                        borderWidth: 1
                    }}
                }},
                scales: {{
                    x: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Time'
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.1)'
                        }}
                    }},
                    y: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Pressure (hPa)'
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.1)'
                        }},
                        beginAtZero: false
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }}
            }}
        }});

        // Auto-refresh every 30 seconds
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>"""
    
    # Write HTML file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML dashboard generated successfully: {output_path}")
        return output_path
    except Exception as e:
        raise IOError(f"Error writing HTML file: {e}")


class DemoHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler to serve the demo dashboard.
    Redirects root requests to the demo dashboard HTML file.
    """
    
    def do_GET(self):
        """Handle GET requests, redirecting root to demo dashboard."""
        if self.path == '/':
            # Redirect root to demo dashboard
            self.path = '/demo_dashboard.html'
        
        # Call parent method to serve the file
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Custom logging to show requests in console."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


def check_port_available(port: int) -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: Starting port number
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number
        
    Raises:
        RuntimeError: If no available port found
    """
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    
    # If no port found, suggest alternative ports
    alternative_ports = [8080, 3000, 5000, 9000, 4000]
    for alt_port in alternative_ports:
        if check_port_available(alt_port):
            print(f"⚠️  Port {start_port} not available, using alternative port {alt_port}")
            return alt_port
    
    raise RuntimeError(f"No available port found. Tried: {list(range(start_port, start_port + max_attempts)) + alternative_ports}")


def open_browser(url: str, delay: float = 1.0):
    """
    Open URL in default browser after a delay.
    
    Args:
        url: URL to open
        delay: Delay in seconds before opening
    """
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"🌐 Opened dashboard in browser: {url}")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"   Please manually open: {url}")
    
    threading.Thread(target=_open, daemon=True).start()


def main():
    """
    Main function to run the dependency-free demo.
    
    Returns:
        0 on success, 1 on error
    """
    print("🚀 Dependency-Free Sensor Data Dashboard Demo")
    print("=" * 50)
    
    try:
        # Check for processed data file
        csv_path = "../data/simulated_processed.csv"
        if not os.path.exists(csv_path):
            print(f"❌ Error: Processed data file not found: {csv_path}")
            print("\n💡 To generate demo data, run:")
            print("   python pipeline/etl_pipeline.py")
            print("\n   Or use the complete demo:")
            print("   python demo/run_demo.py --full")
            return 1
        
        # Load demo data
        data, kpis = load_demo_data(csv_path)
        
        if not data:
            print("❌ Error: No data loaded from CSV file")
            return 1
        
        # Generate HTML dashboard
        html_path = "demo_dashboard.html"
        generate_html(data, kpis, html_path)
        
        # Find available port
        port = find_available_port(8000)
        print(f"🔍 Found available port: {port}")
        
        # Start HTTP server
        try:
            with socketserver.TCPServer(("", port), DemoHandler) as httpd:
                print(f"🌐 Starting HTTP server on port {port}...")
                print(f"📊 Dashboard URL: http://localhost:{port}")
                print("🛑 Press Ctrl+C to stop the server")
                print()
                
                # Open browser
                open_browser(f"http://localhost:{port}")
                
                # Serve requests
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n👋 Server stopped by user")
                except Exception as e:
                    print(f"❌ Server error: {e}")
                    return 1
        except OSError as e:
            print(f"❌ Failed to start server on port {port}: {e}")
            print(f"💡 Try a different port or check if another service is using port {port}")
            return 1
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Data error: {e}")
        return 1
    except IOError as e:
        print(f"❌ I/O error: {e}")
        return 1
    except RuntimeError as e:
        print(f"❌ Runtime error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run demo
    exit_code = main()
    sys.exit(exit_code) 