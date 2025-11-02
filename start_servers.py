#!/usr/bin/env python3
"""
Script untuk menjalankan Line Bot dan AI Agent API server secara bersamaan
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_ai_agent_api(self):
        """Start AI Agent API server"""
        print("🚀 Starting AI Agent API Server...")
        
        # We're already in AI Agent directory
        current_dir = Path.cwd()
        print(f"📁 Current directory: {current_dir}")
        
        # Check if virtual environment exists
        venv_path = current_dir / "venv"
        if venv_path.exists():
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                python_exe = venv_path / "bin" / "python"
                
            if python_exe.exists():
                print(f"🐍 Using Python: {python_exe}")
                process = subprocess.Popen(
                    [str(python_exe), "api_server.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return process
            else:
                print("❌ Python executable not found in virtual environment")
                return None
        else:
            print("❌ Virtual environment not found in AI Agent directory")
            return None
    
    def start_line_bot(self):
        """Start Line Bot server"""
        print("🤖 Starting Line Bot Server...")
        
        # Change to Line Bot directory (go up one level first)
        line_bot_dir = Path.cwd().parent / "Line Bot"
        if not line_bot_dir.exists():
            print("❌ Line Bot directory not found!")
            return None
            
        os.chdir(line_bot_dir)
        
        # Check if app.py exists
        if not (line_bot_dir / "app.py").exists():
            print("❌ app.py not found in Line Bot directory!")
            return None
            
        # Start Line Bot server
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    
    def monitor_process(self, process, name):
        """Monitor a process and print its output"""
        while self.running and process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(f"[{name}] {output.strip()}")
            error = process.stderr.readline()
            if error:
                print(f"[{name} ERROR] {error.strip()}")
    
    def start_servers(self):
        """Start both servers"""
        print("🎯 Starting RIG Chat System...")
        print("=" * 50)
        
        # Start AI Agent API first
        ai_process = self.start_ai_agent_api()
        if ai_process:
            self.processes.append(ai_process)
            print("✅ AI Agent API process started")
            
            # Start monitoring thread for AI Agent
            ai_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(ai_process, "AI-API")
            )
            ai_monitor.daemon = True
            ai_monitor.start()
        else:
            print("❌ Failed to start AI Agent API")
            return
        
        # Wait a bit for AI Agent to initialize
        print("⏳ Waiting for AI Agent to initialize...")
        time.sleep(5)
        
        # Start Line Bot
        line_process = self.start_line_bot()
        if line_process:
            self.processes.append(line_process)
            print("✅ Line Bot process started")
            
            # Start monitoring thread for Line Bot
            line_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(line_process, "LINE-BOT")
            )
            line_monitor.daemon = True
            line_monitor.start()
        else:
            print("❌ Failed to start Line Bot")
            return
        
        print("\n🎉 Both servers are running!")
        print("📡 AI Agent API: http://localhost:5000")
        print("🤖 Line Bot: http://localhost:3030")
        print("📱 Line Bot Webhook: http://localhost:3030/callback")
        print("\n💡 Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
                # Check if any process has died
                for process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️ Process {process.pid} has stopped")
                        self.running = False
                        break
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            self.stop_servers()
    
    def stop_servers(self):
        """Stop all running servers"""
        self.running = False
        
        for process in self.processes:
            if process.poll() is None:  # Process is still running
                print(f"🛑 Stopping process {process.pid}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Force killing process {process.pid}...")
                    process.kill()
        
        print("✅ All servers stopped")

def main():
    """Main function"""
    manager = ServerManager()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        manager.stop_servers()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        manager.start_servers()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        manager.stop_servers()

if __name__ == "__main__":
    main() 