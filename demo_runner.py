#!/usr/bin/env python3
"""
Standalone Demo Runner
"""

import os
import sys
import csv
import json
import time
import webbrowser
import threading
from datetime import datetime
from typing import Dict, List, Tuple

def load_demo_data(csv_path: str = "data/simulated_processed.csv") -> Tuple[List[Dict], Dict]:
    """Load demo data from CSV"""
    print(f"Loading demo data from {csv_path}...")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Demo data file not found: {csv_path}")
    
    data = []
    total_temp = 0.0
    alert_count = 0
    max_uptime = 0
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        lines = csvfile.readlines()
        data_lines = [line for line in lines if not line.strip().startswith('#')]
        
        from io import StringIO
        csv_content = StringIO(''.join(data_lines))
        reader = csv.DictReader(csv_content)
        
        for row in reader:
            try:
                row['temperature'] = float(row['temperature'])
                row['pressure'] = float(row['pressure'])
                row['uptime'] = float(row['uptime'])
                
                # Handle timestamp
                if 'timestamp' in row and row['timestamp']:
                    timestamp_str = row['timestamp']
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            timestamp = datetime.now()
                    
                    row['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                # Check for alerts
                if 'alert_status' in row and row['alert_status'] == 'red':
                    alert_count += 1
                
                total_temp += row['temperature']
                max_uptime = max(max_uptime, row['uptime'])
                
                data.append(row)
                
            except (ValueError, KeyError) as e:
                continue
    
    avg_temp = total_temp / len(data) if data else 0.0
    
    kpis = {
        'avg_temp': round(avg_temp, 2),
        'alert_count': alert_count,
        'uptime_hours': max_uptime,
        'total_records': len(data)
    }
    
    print(f"✅ Successfully loaded {len(data)} data records")
    print(f"📊 KPIs computed: avg_temp={kpis['avg_temp']}°C, alerts={kpis['alert_count']}, uptime={kpis['uptime_hours']}h")
    
    return data, kpis

def generate_html(data: List[Dict], kpis: Dict) -> str:
    """Generate HTML dashboard"""
    print("Generating HTML dashboard...")
    
    timestamps = []
    temperatures = []
    pressures = []
    
    for row in data:
        timestamps.append(row.get('timestamp', ''))
        temperatures.append(row.get('temperature', 0))
        pressures.append(row.get('pressure', 0))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Sensor Data Dashboard Demo</title>
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
        .kpi-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .chart-section {{
            padding: 30px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Smart Sensor Data Dashboard Demo</h1>
            <p>Real-time monitoring of industrial propulsion test rig sensors</p>
        </div>
        
        <div class="kpi-section">
            <h2>Key Performance Indicators</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['avg_temp']}°C</div>
                    <div>Average Temperature</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['alert_count']}</div>
                    <div>Alert Count</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['uptime_hours']}h</div>
                    <div>Total Uptime</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpis['total_records']}</div>
                    <div>Total Records</div>
                </div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-container">
                <h3>Temperature Trend</h3>
                <canvas id="tempChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Pressure Trend</h3>
                <canvas id="pressureChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Temperature Chart
        const tempCtx = document.getElementById('tempChart').getContext('2d');
        new Chart(tempCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timestamps)},
                datasets: [{{
                    label: 'Temperature (°C)',
                    data: {json.dumps(temperatures)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Pressure Chart
        const pressureCtx = document.getElementById('pressureChart').getContext('2d');
        new Chart(pressureCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timestamps)},
                datasets: [{{
                    label: 'Pressure (kPa)',
                    data: {json.dumps(pressures)},
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    html_path = "demo_dashboard.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML dashboard generated: {html_path}")
    return html_path

def start_server(html_path: str):
    """Start HTTP server"""
    import http.server
    import socketserver
    
    # Find available port
    port = 8001
    for test_port in range(8001, 8010):
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', test_port))
                port = test_port
                break
        except OSError:
            continue
    
    print(f"🌐 Starting server on port {port}...")
    
    # Custom handler
    class DemoHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/demo_dashboard.html'
            return super().do_GET()
        
        def log_message(self, format, *args):
            print(f"[{time.strftime('%H:%M:%S')}] {format % args}")
    
    # Start server
    with socketserver.TCPServer(("", port), DemoHandler) as httpd:
        print(f"✅ Server started! Dashboard available at: http://localhost:{port}")
        print("🛑 Press Ctrl+C to stop")
        
        # Open browser
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f"http://localhost:{port}")
                print(f"🌐 Opened browser: http://localhost:{port}")
            except:
                print(f"💡 Please manually open: http://localhost:{port}")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")

def main():
    """Main function"""
    print("🚀 Smart Sensor Data Dashboard Demo")
    print("=" * 50)
    
    try:
        # Load data
        data, kpis = load_demo_data()
        
        # Generate HTML
        html_path = generate_html(data, kpis)
        
        # Start server
        start_server(html_path)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 