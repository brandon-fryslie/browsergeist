#!/usr/bin/env python3
"""
BrowserGeist CLI - Professional Command Line Interface

A comprehensive CLI tool for managing BrowserGeist automation workflows,
daemon services, system health checks, and configuration.
"""

import sys
import os
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import socket
import time

# Add the parent directory to the path so we can import browsergeist
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from python_sdk.browsergeist import HumanMouse, MotionProfiles
    from python_sdk.async_browsergeist import AsyncHumanMouse
except ImportError as e:
    print(f"❌ Failed to import BrowserGeist modules: {e}")
    print("   Make sure the project is built and dependencies are installed.")
    sys.exit(1)
from cli.commands import CLICommands

class BrowserGeistCLI(CLICommands):
    """Main CLI class for BrowserGeist automation framework."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".browsergeist"
        self.config_file = self.config_dir / "config.json"
        self.log_dir = self.config_dir / "logs"
        self.daemon_socket = "/tmp/browsergeist.sock"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "daemon": {
                "socket_path": "/tmp/browsergeist.sock",
                "auto_start": True,
                "timeout": 30.0
            },
            "motion": {
                "default_profile": "Natural",
                "custom_profiles": {}
            },
            "vision": {
                "template_cache_ttl": 300,
                "confidence_threshold": 0.8
            },
            "captcha": {
                "default_methods": ["openai", "manual", "twocaptcha"],
                "openai_api_key": None,
                "twocaptcha_api_key": None
            },
            "logging": {
                "level": "INFO",
                "format": "structured",
                "console_output": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_config, **config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration.")
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config["logging"]["level"])
        log_format = self.config["logging"]["format"]
        
        if log_format == "structured":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"module": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # File handler
        log_file = self.log_dir / f"browsergeist-{int(time.time())}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Console handler (if enabled)
        handlers = [file_handler]
        if self.config["logging"]["console_output"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)
        
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
        
        self.logger = logging.getLogger("browsergeist.cli")
    
    def _is_daemon_running(self) -> bool:
        """Check if the BrowserGeist daemon is running."""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(self.daemon_socket)
            sock.close()
            return True
        except (socket.error, FileNotFoundError):
            return False
    
    def _start_daemon(self) -> bool:
        """Start the BrowserGeist daemon."""
        daemon_path = Path(__file__).parent.parent.parent / "bin" / "browsergeist-daemon"
        
        if not daemon_path.exists():
            print(f"❌ Daemon binary not found at: {daemon_path}")
            print("   Please build the project first: make build")
            return False
        
        try:
            print("🚀 Starting BrowserGeist daemon...")
            process = subprocess.Popen([str(daemon_path)], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            # Wait for daemon to start
            for _ in range(50):  # 5 second timeout
                if self._is_daemon_running():
                    print("✅ Daemon started successfully")
                    return True
                time.sleep(0.1)
            
            print("❌ Daemon failed to start within timeout")
            return False
            
        except subprocess.SubprocessError as e:
            print(f"❌ Failed to start daemon: {e}")
            return False
    
    def _stop_daemon(self) -> bool:
        """Stop the BrowserGeist daemon."""
        try:
            # Send stop command via socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.daemon_socket)
            sock.send(b'{"command": "stop"}')
            sock.close()
            
            # Wait for daemon to stop
            for _ in range(50):  # 5 second timeout
                if not self._is_daemon_running():
                    print("✅ Daemon stopped successfully")
                    return True
                time.sleep(0.1)
            
            print("⚠️ Daemon did not stop gracefully, may need manual termination")
            return False
            
        except socket.error as e:
            print(f"❌ Failed to stop daemon: {e}")
            return False

def main():
    """Main CLI entry point."""
    cli = BrowserGeistCLI()
    
    parser = argparse.ArgumentParser(
        prog="browsergeist",
        description="BrowserGeist - Professional Browser Automation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  browsergeist run script.py --profile=fast
  browsergeist doctor
  browsergeist daemon start
  browsergeist daemon stop
  browsergeist daemon status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run automation script")
    run_parser.add_argument("script", help="Python script to execute")
    run_parser.add_argument("--profile", 
                           choices=["Natural", "Careful", "Fast"], 
                           default="Natural",
                           help="Motion profile to use")
    run_parser.add_argument("--async", action="store_true", 
                           help="Use async execution")
    run_parser.add_argument("--timeout", type=float, default=30.0,
                           help="Command timeout in seconds")
    run_parser.add_argument("--verbose", "-v", action="store_true",
                           help="Verbose output")
    
    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="System health check")
    doctor_parser.add_argument("--fix", action="store_true",
                              help="Attempt to fix found issues")
    
    # Daemon command
    daemon_parser = subparsers.add_parser("daemon", help="Daemon management")
    daemon_subparsers = daemon_parser.add_subparsers(dest="daemon_action")
    daemon_subparsers.add_parser("start", help="Start daemon")
    daemon_subparsers.add_parser("stop", help="Stop daemon")
    daemon_subparsers.add_parser("status", help="Show daemon status")
    daemon_subparsers.add_parser("restart", help="Restart daemon")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    config_subparsers.add_parser("show", help="Show current configuration")
    config_subparsers.add_parser("edit", help="Edit configuration file")
    config_set_parser = config_subparsers.add_parser("set", help="Set config value")
    config_set_parser.add_argument("key", help="Configuration key")
    config_set_parser.add_argument("value", help="Configuration value")
    
    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Interactive debugging mode")
    debug_parser.add_argument("--screenshot", action="store_true",
                             help="Take screenshot and show vision analysis")
    debug_parser.add_argument("--test-motion", action="store_true",
                             help="Test motion profiles interactively")
    debug_parser.add_argument("--test-captcha", action="store_true",
                             help="Test CAPTCHA detection and solving")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "run":
            return cli.cmd_run(args)
        elif args.command == "doctor":
            return cli.cmd_doctor(args)
        elif args.command == "daemon":
            return cli.cmd_daemon(args)
        elif args.command == "config":
            return cli.cmd_config(args)
        elif args.command == "debug":
            return cli.cmd_debug(args)
        elif args.command == "version":
            return cli.cmd_version(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 130
    except Exception as e:
        cli.logger.error(f"CLI error: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
