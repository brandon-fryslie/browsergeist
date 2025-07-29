"""
BrowserGeist CLI Commands

Implementation of all CLI commands including run, doctor, daemon management,
and configuration handling.
"""

import sys
import os
import json
import subprocess
import socket
import time
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util
import tempfile

class CLICommands:
    """Command implementations for BrowserGeist CLI."""
    
    def cmd_run(self, args) -> int:
        """Run automation script command."""
        script_path = Path(args.script)
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return 1
        
        if not script_path.suffix == '.py':
            print(f"❌ Script must be a Python file (.py): {script_path}")
            return 1
        
        # Check daemon status
        if not self._is_daemon_running():
            if self.config["daemon"]["auto_start"]:
                print("🔄 Daemon not running, starting automatically...")
                if not self._start_daemon():
                    return 1
            else:
                print("❌ Daemon not running. Start it with: browsergeist daemon start")
                return 1
        
        print(f"🚀 Running script: {script_path}")
        print(f"📊 Profile: {args.profile}")
        async_mode = 'Yes' if getattr(args, 'async', False) else 'No'
        print(f"⚡ Async: {async_mode}")
        print(f"⏱️ Timeout: {args.timeout}s")
        
        try:
            # Load and execute the script
            spec = importlib.util.spec_from_file_location("user_script", script_path)
            if spec is None or spec.loader is None:
                print(f"❌ Could not load script: {script_path}")
                return 1
            
            module = importlib.util.module_from_spec(spec)
            
            # Set up environment variables for the script
            os.environ["BROWSERGEIST_PROFILE"] = args.profile
            os.environ["BROWSERGEIST_TIMEOUT"] = str(args.timeout)
            os.environ["BROWSERGEIST_ASYNC"] = "1" if getattr(args, 'async', False) else "0"
            
            # Execute the script
            spec.loader.exec_module(module)
            
            print("✅ Script execution completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            print(f"❌ Script execution failed: {e}")
            return 1
    
    def cmd_doctor(self, args) -> int:
        """System health check command."""
        print("🏥 BrowserGeist System Health Check")
        print("=" * 50)
        
        issues = []
        checks = [
            ("Daemon Binary", self._check_daemon_binary),
            ("Daemon Running", self._check_daemon_running),
            ("Python Dependencies", self._check_python_deps),
            ("System Permissions", self._check_permissions),
            ("Configuration", self._check_configuration),
            ("Socket Connectivity", self._check_socket_connectivity),
            ("Build Status", self._check_build_status),
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔍 Checking {check_name}...")
            try:
                result = check_func()
                if result["status"] == "ok":
                    print(f"✅ {result['message']}")
                elif result["status"] == "warning":
                    print(f"⚠️ {result['message']}")
                    if args.fix and "fix" in result:
                        print(f"🔧 Attempting to fix...")
                        if result["fix"]():
                            print(f"✅ Fixed successfully")
                        else:
                            print(f"❌ Fix failed")
                            issues.append(check_name)
                else:  # error
                    print(f"❌ {result['message']}")
                    issues.append(check_name)
                    if args.fix and "fix" in result:
                        print(f"🔧 Attempting to fix...")
                        if result["fix"]():
                            print(f"✅ Fixed successfully")
                            issues.remove(check_name)
                        else:
                            print(f"❌ Fix failed")
            except Exception as e:
                print(f"❌ Check failed: {e}")
                issues.append(check_name)
        
        print(f"\n📋 Health Check Summary")
        print("=" * 30)
        if not issues:
            print("✅ All checks passed! System is healthy.")
            return 0
        else:
            print(f"⚠️ {len(issues)} issue(s) found:")
            for issue in issues:
                print(f"   • {issue}")
            print(f"\nRun with --fix to attempt automatic fixes.")
            return 1
    
    def cmd_daemon(self, args) -> int:
        """Daemon management command."""
        if not args.daemon_action:
            print("❌ No daemon action specified")
            print("Available actions: start, stop, status, restart")
            return 1
        
        if args.daemon_action == "start":
            if self._is_daemon_running():
                print("✅ Daemon is already running")
                return 0
            else:
                return 0 if self._start_daemon() else 1
        
        elif args.daemon_action == "stop":
            if not self._is_daemon_running():
                print("ℹ️ Daemon is not running")
                return 0
            else:
                return 0 if self._stop_daemon() else 1
        
        elif args.daemon_action == "status":
            if self._is_daemon_running():
                print("✅ Daemon is running")
                
                # Get process info
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                        if 'browsergeist-daemon' in proc.info['name']:
                            create_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                      time.localtime(proc.info['create_time']))
                            print(f"   PID: {proc.info['pid']}")
                            print(f"   Started: {create_time}")
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Test socket connectivity
                try:
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    sock.connect(self.daemon_socket)
                    sock.close()
                    print("   Socket: ✅ Responsive")
                except socket.error:
                    print("   Socket: ❌ Not responding")
                
                return 0
            else:
                print("❌ Daemon is not running")
                return 1
        
        elif args.daemon_action == "restart":
            print("🔄 Restarting daemon...")
            if self._is_daemon_running():
                if not self._stop_daemon():
                    return 1
                time.sleep(1)  # Brief pause
            return 0 if self._start_daemon() else 1
        
        else:
            print(f"❌ Unknown daemon action: {args.daemon_action}")
            return 1
    
    def cmd_config(self, args) -> int:
        """Configuration management command."""
        if not args.config_action:
            print("❌ No config action specified")
            print("Available actions: show, edit, set")
            return 1
        
        if args.config_action == "show":
            print("📋 BrowserGeist Configuration")
            print("=" * 35)
            print(json.dumps(self.config, indent=2))
            print(f"\nConfig file: {self.config_file}")
            return 0
        
        elif args.config_action == "edit":
            try:
                # Use system default editor
                editor = os.environ.get('EDITOR', 'nano')
                subprocess.run([editor, str(self.config_file)])
                
                # Reload config after editing
                self.config = self._load_config()
                print("✅ Configuration updated")
                return 0
            except subprocess.SubprocessError as e:
                print(f"❌ Failed to open editor: {e}")
                return 1
        
        elif args.config_action == "set":
            try:
                # Parse key path (e.g., "daemon.timeout")
                keys = args.key.split('.')
                value = args.value
                
                # Try to parse value as JSON (for numbers, booleans, etc.)
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string
                
                # Navigate to the config section
                config_section = self.config
                for key in keys[:-1]:
                    if key not in config_section:
                        config_section[key] = {}
                    config_section = config_section[key]
                
                # Set the value
                config_section[keys[-1]] = value
                
                # Save updated config
                self._save_config(self.config)
                print(f"✅ Set {args.key} = {value}")
                return 0
                
            except Exception as e:
                print(f"❌ Failed to set config value: {e}")
                return 1
        
        else:
            print(f"❌ Unknown config action: {args.config_action}")
            return 1
    
    def cmd_debug(self, args) -> int:
        """Interactive debugging mode."""
        print("🐛 BrowserGeist Interactive Debug Mode")
        print("=" * 45)
        
        if not self._is_daemon_running():
            print("❌ Daemon is not running. Start it with: browsergeist daemon start")
            return 1
        
        if args.screenshot:
            return self._debug_screenshot()
        elif args.test_motion:
            return self._debug_motion()
        elif args.test_captcha:
            return self._debug_captcha()
        else:
            # Interactive menu
            return self._debug_interactive()
    
    def _debug_screenshot(self) -> int:
        """Debug screenshot and vision analysis."""
        print("📸 Taking screenshot and analyzing...")
        
        try:
            # Import modules here to avoid import issues
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from python_sdk.browsergeist import HumanMouse
            
            with HumanMouse() as bot:
                # Take screenshot and save it
                result = bot._send_command({"action": "screenshot"})
                if result.success:
                    screenshot_data = result.data.get("image")
                    if screenshot_data:
                        import base64
                        image_bytes = base64.b64decode(screenshot_data)
                        screenshot_path = Path.home() / "browsergeist_debug_screenshot.png"
                        with open(screenshot_path, "wb") as f:
                            f.write(image_bytes)
                        print(f"✅ Screenshot saved to: {screenshot_path}")
                        print("   You can open this file to see what BrowserGeist sees")
                    else:
                        print("❌ No screenshot data received")
                        return 1
                else:
                    print(f"❌ Failed to take screenshot: {result.error_message}")
                    return 1
            
            return 0
        except Exception as e:
            print(f"❌ Screenshot debug failed: {e}")
            return 1
    
    def _debug_motion(self) -> int:
        """Debug motion profiles interactively."""
        print("🎯 Interactive Motion Testing")
        print("This will move the mouse cursor to test motion profiles.")
        
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from python_sdk.browsergeist import HumanMouse, MotionProfiles
            
            profiles = {
                "1": ("Natural", MotionProfiles.NATURAL),
                "2": ("Careful", MotionProfiles.CAREFUL), 
                "3": ("Fast", MotionProfiles.FAST)
            }
            
            print("\nAvailable motion profiles:")
            for key, (name, _) in profiles.items():
                print(f"  {key}. {name}")
            
            choice = input("\nSelect profile (1-3) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return 0
            
            if choice not in profiles:
                print("❌ Invalid choice")
                return 1
            
            profile_name, profile = profiles[choice]
            print(f"📍 Using {profile_name} profile")
            print("🎯 Move your mouse to where you want to test movement, then press Enter...")
            input()
            
            # Get current cursor position as start point
            import subprocess
            result = subprocess.run(['osascript', '-e', 'tell application "System Events" to return (current application\'s NSEvent\'s mouseLocation)'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the result and move to a nearby location
                print("🤖 Moving mouse with human-like motion...")
                
                with HumanMouse() as bot:
                    # Move to a point 200 pixels to the right and 100 down
                    bot.move_to((500, 300), profile)
                    print("✅ Motion test completed!")
            else:
                print("❌ Could not get cursor position")
                return 1
            
            return 0
        except Exception as e:
            print(f"❌ Motion debug failed: {e}")
            return 1
    
    def _debug_captcha(self) -> int:
        """Debug CAPTCHA detection and solving."""
        print("🔐 CAPTCHA Detection and Solving Test")
        print("This will analyze the current screen for CAPTCHAs.")
        
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from python_sdk.browsergeist import HumanMouse
            
            with HumanMouse(auto_solve_captcha=True) as bot:
                print("🔍 Scanning for CAPTCHAs...")
                solution = bot.check_for_captcha()
                
                if solution is None:
                    print("✅ No CAPTCHA detected on current screen")
                elif solution.success:
                    print(f"🎯 CAPTCHA detected and solved!")
                    print(f"   Method: {solution.method}")
                    print(f"   Solution: {solution.solution or 'Coordinate-based'}")
                else:
                    print(f"❌ CAPTCHA detected but solving failed: {solution.error}")
            
            return 0
        except Exception as e:
            print(f"❌ CAPTCHA debug failed: {e}")
            return 1
    
    def _debug_interactive(self) -> int:
        """Interactive debugging menu."""
        while True:
            print("\n🐛 Debug Options:")
            print("  1. Take screenshot and analyze")
            print("  2. Test motion profiles")
            print("  3. Test CAPTCHA detection")
            print("  4. System status check")
            print("  q. Quit")
            
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q':
                print("👋 Exiting debug mode")
                return 0
            elif choice == '1':
                self._debug_screenshot()
            elif choice == '2':
                self._debug_motion()
            elif choice == '3':
                self._debug_captcha()
            elif choice == '4':
                # Quick status check
                print("\n📊 System Status:")
                print(f"   Daemon: {'✅ Running' if self._is_daemon_running() else '❌ Not running'}")
                
                # Check socket
                try:
                    import socket
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    sock.connect(self.daemon_socket)
                    sock.close()
                    print("   Socket: ✅ Responsive")
                except:
                    print("   Socket: ❌ Not responding")
            else:
                print("❌ Invalid option")

    def cmd_version(self, args) -> int:
        """Show version information."""
        print("🤖 BrowserGeist - Professional Browser Automation Framework")
        print("=" * 65)
        print("Version: 1.0.0-production")
        print("Build: Enhanced Virtual Drivers with Stealth Validation")
        print("Python SDK: Async/Await + Enhanced Error Handling")
        print("Motion Engine: Advanced Fitts' Law + Bézier Curves")
        print("Vision System: Multi-scale Template Matching")
        print("CAPTCHA System: OpenAI + Manual + 2Captcha")
        print("Stealth Score: 70/100 (Good level)")
        print()
        print("Repository: https://github.com/browsergeist/browsergeist")
        print("Documentation: https://browsergeist.dev/docs")
        print("License: MIT")
        return 0
    
    # Health check helper methods
    def _check_daemon_binary(self) -> Dict[str, Any]:
        """Check if daemon binary exists and is executable."""
        daemon_path = Path(__file__).parent.parent.parent / "bin" / "browsergeist-daemon"
        
        if not daemon_path.exists():
            return {
                "status": "error",
                "message": f"Daemon binary not found at: {daemon_path}",
                "fix": lambda: self._build_project()
            }
        
        if not os.access(daemon_path, os.X_OK):
            return {
                "status": "error", 
                "message": "Daemon binary is not executable",
                "fix": lambda: os.chmod(daemon_path, 0o755)
            }
        
        return {"status": "ok", "message": "Daemon binary found and executable"}
    
    def _check_daemon_running(self) -> Dict[str, Any]:
        """Check if daemon is running."""
        if self._is_daemon_running():
            return {"status": "ok", "message": "Daemon is running"}
        else:
            return {
                "status": "warning",
                "message": "Daemon is not running",
                "fix": lambda: self._start_daemon()
            }
    
    def _check_python_deps(self) -> Dict[str, Any]:
        """Check if required Python dependencies are installed."""
        required_deps = ["opencv-python", "numpy", "pillow", "pytesseract", "requests", "flask"]
        missing_deps = []
        
        for dep in required_deps:
            try:
                __import__(dep.replace("-", "_"))
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            return {
                "status": "error",
                "message": f"Missing dependencies: {', '.join(missing_deps)}",
                "fix": lambda: self._install_deps(missing_deps)
            }
        
        return {"status": "ok", "message": "All Python dependencies installed"}
    
    def _check_permissions(self) -> Dict[str, Any]:
        """Check system permissions."""
        # This is a simplified check - in production you'd check macOS TCC permissions
        socket_dir = Path(self.daemon_socket).parent
        
        if not os.access(socket_dir, os.W_OK):
            return {
                "status": "error",
                "message": f"No write access to socket directory: {socket_dir}"
            }
        
        return {"status": "ok", "message": "Basic system permissions OK"}
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity."""
        try:
            # Basic config validation
            if not isinstance(self.config.get("daemon", {}), dict):
                return {"status": "error", "message": "Invalid daemon configuration"}
            
            if not isinstance(self.config.get("motion", {}), dict):
                return {"status": "error", "message": "Invalid motion configuration"}
            
            return {"status": "ok", "message": "Configuration is valid"}
        except Exception as e:
            return {"status": "error", "message": f"Configuration error: {e}"}
    
    def _check_socket_connectivity(self) -> Dict[str, Any]:
        """Check socket connectivity."""
        if not self._is_daemon_running():
            return {"status": "warning", "message": "Cannot test socket - daemon not running"}
        
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect(self.daemon_socket)
            sock.close()
            return {"status": "ok", "message": "Socket connectivity OK"}
        except socket.error as e:
            return {"status": "error", "message": f"Socket connectivity failed: {e}"}
    
    def _check_build_status(self) -> Dict[str, Any]:
        """Check if project is properly built."""
        expected_files = [
            "bin/browsergeist-daemon",
            "src/python_sdk/browsergeist.py",
            "src/vision/template_matcher.py"
        ]
        
        project_root = Path(__file__).parent.parent.parent
        missing_files = []
        
        for file_path in expected_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return {
                "status": "error",
                "message": f"Missing build files: {', '.join(missing_files)}",
                "fix": lambda: self._build_project()
            }
        
        return {"status": "ok", "message": "Project build files present"}
    
    def _build_project(self) -> bool:
        """Attempt to build the project."""
        try:
            project_root = Path(__file__).parent.parent.parent
            result = subprocess.run(["make", "build"], 
                                  cwd=project_root, 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False
    
    def _install_deps(self, deps: List[str]) -> bool:
        """Attempt to install missing dependencies."""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + deps,
                          check=True, capture_output=True)
            return True
        except subprocess.SubprocessError:
            return False
