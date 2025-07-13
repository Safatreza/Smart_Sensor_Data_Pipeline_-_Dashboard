#!/usr/bin/env python3
"""
Direct Demo Runner - Bypasses terminal issues
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading

def run_demo():
    """Run the demo directly"""
    print("🚀 Starting Demo Dashboard...")
    print("=" * 50)
    
    # Change to demo directory
    demo_dir = os.path.join(os.getcwd(), "demo")
    os.chdir(demo_dir)
    
    # Check if demo data exists
    csv_path = "../data/simulated_processed.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Demo data not found: {csv_path}")
        print("💡 Please ensure the ETL pipeline has been run first.")
        return False
    
    print(f"✅ Found demo data: {csv_path}")
    
    # Import and run demo functions
    try:
        from run_demo import load_demo_data, generate_html, find_available_port, open_browser
        import http.server
        import socketserver
        
        # Load data
        print("📊 Loading demo data...")
        data, kpis = load_demo_data(csv_path)
        
        # Generate HTML
        print("🌐 Generating dashboard...")
        html_path = "demo_dashboard.html"
        generate_html(data, kpis, html_path)
        
        # Find available port
        port = find_available_port(8000)
        print(f"🔍 Using port: {port}")
        
        # Start server
        print(f"🌐 Starting server on port {port}...")
        
        # Custom handler to redirect root to demo
        class DemoHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/demo_dashboard.html'
                return super().do_GET()
            
            def log_message(self, format, *args):
                print(f"[{time.strftime('%H:%M:%S')}] {format % args}")
        
        # Start server in background
        with socketserver.TCPServer(("", port), DemoHandler) as httpd:
            print(f"✅ Server started! Dashboard available at: http://localhost:{port}")
            print("🛑 Press Ctrl+C to stop")
            
            # Open browser
            def open_browser_delayed():
                time.sleep(2)
                try:
                    webbrowser.open(f"http://localhost:{port}")
                    print(f"🌐 Opened browser: http://localhost:{port}")
                except:
                    print(f"💡 Please manually open: http://localhost:{port}")
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
            
            # Serve requests
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n👋 Demo stopped by user")
                return True
            except Exception as e:
                print(f"❌ Server error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

if __name__ == "__main__":
    success = run_demo()
    if not success:
        input("Press Enter to exit...") 