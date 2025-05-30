#!/usr/bin/env python3
"""
Hospital A2A System Launcher
Simple script to start all agents and run demos
"""

import subprocess
import time
import sys
import os
import signal
import threading
from typing import List, Optional

class HospitalA2ALauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.script_name = "hospital_a2a_system.py"
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        required_packages = ["fastapi", "uvicorn", "httpx", "pydantic"]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - Not installed")
                print(f"\nPlease install missing dependencies:")
                print(f"pip install {' '.join(required_packages)}")
                return False
        
        print("✅ All dependencies installed!")
        return True
    
    def check_script_exists(self):
        """Check if the main script exists"""
        if not os.path.exists(self.script_name):
            print(f"❌ {self.script_name} not found!")
            print("Please ensure the hospital_a2a_system.py file is in the current directory.")
            return False
        return True

    def check_ports(self):
        """Check if required ports are available"""
        print("🔍 Checking port availability...")
        import socket
        
        ports = [8000, 8001, 8002, 8003]
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(f"  ❌ Port {port} is already in use")
                    return False
                else:
                    print(f"  ✅ Port {port} available")
            except Exception as e:
                print(f"  ⚠️  Port {port} check failed: {e}")
        
        return True
    
    def start_agent(self, agent_type: str, port: int) -> Optional[subprocess.Popen]:
        """Start a single agent"""
        try:
            print(f"🚀 Starting {agent_type} agent on port {port}...")
            process = subprocess.Popen(
                [sys.executable, self.script_name, agent_type],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.processes.append(process)
            return process
        except Exception as e:
            print(f"❌ Failed to start {agent_type} agent: {e}")
            return None
    
    def wait_for_agents(self, timeout: int = 30):
        """Wait for all agents to be ready"""
        print("⏳ Waiting for agents to initialize...")
        
        import socket
        ports = [8000, 8001, 8002, 8003]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ready_count = 0
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    if result == 0:
                        ready_count += 1
                except:
                    pass
            
            if ready_count == len(ports):
                print("✅ All agents are ready!")
                return True
            
            print(f"   {ready_count}/{len(ports)} agents ready...")
            time.sleep(2)
        
        print("⚠️  Timeout waiting for agents to start")
        return False
    
    def run_demo(self):
        """Run the demo client"""
        print("\n🎬 Running demonstration...")
        try:
            result = subprocess.run(
                [sys.executable, self.script_name, "demo"],
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
    
    def stop_all_agents(self):
        """Stop all running agents"""
        print("\n🛑 Stopping all agents...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Warning: Error stopping process: {e}")
        
        self.processes.clear()
        print("✅ All agents stopped")
    
    def start_all_agents(self):
        """Start all hospital agents"""
        agents = [
            ("coordinator", 8000),
            ("patient", 8001),
            ("doctor", 8002),
            ("booking", 8003)
        ]
        
        print("\n🏥 Starting Hospital A2A System...")
        print("=" * 50)
        
        for agent_type, port in agents:
            process = self.start_agent(agent_type, port)
            if not process:
                self.stop_all_agents()
                return False
            time.sleep(1)  # Small delay between starts
        
        return self.wait_for_agents()
    
    def interactive_mode(self):
        """Interactive mode for user choices"""
        while True:
            print("\n🏥 Hospital A2A System Launcher")
            print("=" * 40)
            print("1. Start all agents and run demo")
            print("2. Start agents only")
            print("3. Run demo (agents must be running)")
            print("4. Check system status")
            print("5. Stop all agents")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                if self.start_all_agents():
                    self.run_demo()
                    input("\nPress Enter to continue...")
                
            elif choice == "2":
                self.start_all_agents()
                print("\n✅ Agents started! Run option 3 to test or use:")
                print("   python hospital_a2a_system.py demo")
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                self.run_demo()
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                self.check_system_status()
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                self.stop_all_agents()
                input("\nPress Enter to continue...")
                
            elif choice == "6":
                self.stop_all_agents()
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please try again.")
    
    def check_system_status(self):
        """Check the status of all agents"""
        print("\n📊 System Status Check")
        print("=" * 30)
        
        import socket
        agents = [
            ("Coordinator", 8000),
            ("Patient Registration", 8001),
            ("Doctor Availability", 8002),
            ("Appointment Booking", 8003)
        ]
        
        for name, port in agents:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(f"  ✅ {name} (:{port}) - Running")
                else:
                    print(f"  ❌ {name} (:{port}) - Not running")
            except Exception as e:
                print(f"  ⚠️  {name} (:{port}) - Check failed: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Received interrupt signal...")
        self.stop_all_agents()
        sys.exit(0)

def main():
    launcher = HospitalA2ALauncher()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, launcher.signal_handler)
    signal.signal(signal.SIGTERM, launcher.signal_handler)
    
    print("🏥 Hospital A2A System Launcher")
    print("=" * 40)
    
    # Pre-flight checks
    # if not launcher.check_dependencies():
    #     sys.exit(1)
    
    if not launcher.check_script_exists():
        sys.exit(1)
    
    if not launcher.check_ports():
        print("\n⚠️  Some ports are in use. You may need to stop existing processes.")
        choice = input("Continue anyway? (y/N): ").strip().lower()
        if choice != 'y':
            sys.exit(1)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            # Automatic mode - start all and run demo
            print("\n🤖 Auto mode: Starting all agents and running demo...")
            if launcher.start_all_agents():
                launcher.run_demo()
            launcher.stop_all_agents()
        elif sys.argv[1] == "start":
            # Just start agents
            launcher.start_all_agents()
            print("\n✅ All agents started! Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            print("Usage:")
            print(f"  {sys.argv[0]}          - Interactive mode")
            print(f"  {sys.argv[0]} auto     - Auto start and demo")
            print(f"  {sys.argv[0]} start    - Start agents only")
    else:
        # Interactive mode
        launcher.interactive_mode()

if __name__ == "__main__":
    main()