"""
BrowserGeist Async Python SDK

Modern async/await interface for human-like browser automation
with enhanced error handling, connection pooling, and session management.
"""

import asyncio
import socket
import json
import time
import cv2
import numpy as np
import base64
from typing import Optional, Tuple, Union, List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import os
from enum import Enum
import logging
from contextlib import asynccontextmanager

# Add vision module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vision'))
from template_matcher import TemplateMatcher, MatchResult, VisionCache, MultiMonitorMatcher

# Import CAPTCHA solver
from python_sdk.captcha_solver import CaptchaSolver, CaptchaSolveMethod, CaptchaSolution

# Import sync classes for compatibility
from python_sdk.browsergeist import MotionProfile, MotionProfiles


class BrowserGeistError(Exception):
    """Base exception for BrowserGeist operations"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()


class ConnectionError(BrowserGeistError):
    """Connection-related errors"""
    pass


class CommandError(BrowserGeistError):
    """Command execution errors"""
    pass


class VisionError(BrowserGeistError):
    """Vision/template matching errors"""
    pass


class CaptchaError(BrowserGeistError):
    """CAPTCHA solving errors"""
    pass


@dataclass
class CommandResult:
    """Result of a command execution"""
    success: bool
    data: Dict[str, Any]
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class ConnectionPool:
    """Async connection pool for daemon connections"""
    
    def __init__(self, daemon_socket: str, max_connections: int = 5):
        self.daemon_socket = daemon_socket
        self.max_connections = max_connections
        self._connections: List[socket.socket] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()
        
    async def get_connection(self) -> socket.socket:
        """Get a connection from the pool"""
        try:
            # Try to get an existing connection
            conn = self._available.get_nowait()
            return conn
        except asyncio.QueueEmpty:
            async with self._lock:
                if len(self._connections) < self.max_connections:
                    # Create new connection
                    conn = await self._create_connection()
                    self._connections.append(conn)
                    return conn
                else:
                    # Wait for available connection
                    return await self._available.get()
    
    async def return_connection(self, conn: socket.socket):
        """Return connection to pool"""
        await self._available.put(conn)
    
    async def _create_connection(self) -> socket.socket:
        """Create a new connection to daemon"""
        try:
            conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            conn.connect(self.daemon_socket)
            return conn
        except Exception as e:
            raise ConnectionError(f"Failed to create daemon connection: {e}", "CONNECTION_FAILED")
    
    async def close_all(self):
        """Close all connections"""
        async with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except:
                    pass
            self._connections.clear()
            
            # Clear queue
            while not self._available.empty():
                try:
                    conn = self._available.get_nowait()
                    conn.close()
                except:
                    pass


class AsyncHumanMouse:
    """Async interface for human-like mouse automation"""
    
    def __init__(self, 
                 daemon_socket: str = "/tmp/browsergeist.sock",
                 openai_api_key: Optional[str] = None,
                 twocaptcha_api_key: Optional[str] = None,
                 auto_solve_captcha: bool = True,
                 max_connections: int = 5,
                 command_timeout: float = 30.0):
        """
        Initialize async HumanMouse instance
        
        Args:
            daemon_socket: Path to daemon socket
            openai_api_key: OpenAI API key for CAPTCHA solving
            twocaptcha_api_key: 2Captcha API key for CAPTCHA solving
            auto_solve_captcha: Enable automatic CAPTCHA detection/solving
            max_connections: Maximum number of pooled connections
            command_timeout: Timeout for command execution
        """
        self.daemon_socket = daemon_socket
        self.command_timeout = command_timeout
        self.pool = ConnectionPool(daemon_socket, max_connections)
        
        # Vision components
        self.matcher = TemplateMatcher()
        self.multi_monitor = MultiMonitorMatcher()
        self.vision_cache = VisionCache()
        
        # CAPTCHA solving
        self.auto_solve_captcha = auto_solve_captcha
        self.captcha_solver = CaptchaSolver(
            openai_api_key=openai_api_key,
            twocaptcha_api_key=twocaptcha_api_key
        ) if (openai_api_key or twocaptcha_api_key or auto_solve_captcha) else None
        
        # Session state
        self._session_id = None
        self._session_stats = {
            "commands_executed": 0,
            "errors_occurred": 0,
            "session_start": time.time()
        }
        
        # Logging
        self.logger = logging.getLogger("browsergeist")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def start_session(self) -> str:
        """Start a new automation session"""
        self._session_id = f"session_{int(time.time())}_{id(self)}"
        self._session_stats["session_start"] = time.time()
        self.logger.info(f"Started session: {self._session_id}")
        return self._session_id
    
    async def close_session(self):
        """Close the current session and cleanup resources"""
        if self._session_id:
            duration = time.time() - self._session_stats["session_start"]
            self.logger.info(f"Closing session {self._session_id} after {duration:.2f}s")
            self.logger.info(f"Session stats: {self._session_stats}")
        
        await self.pool.close_all()
        self.vision_cache.clear()
        self._session_id = None
    
    async def _send_command(self, command: Dict[str, Any]) -> CommandResult:
        """Send command to daemon with enhanced error handling"""
        start_time = time.time()
        
        try:
            # Get connection from pool
            conn = await asyncio.wait_for(
                self.pool.get_connection(), 
                timeout=self.command_timeout
            )
            
            try:
                # Send command
                message = json.dumps(command).encode('utf-8')
                conn.send(len(message).to_bytes(4, 'big') + message)
                
                # Read response with timeout
                length_bytes = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, conn.recv, 4),
                    timeout=self.command_timeout
                )
                
                length = int.from_bytes(length_bytes, 'big')
                response_bytes = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, conn.recv, length),
                    timeout=self.command_timeout
                )
                
                response = json.loads(response_bytes.decode('utf-8'))
                
                # Return connection to pool
                await self.pool.return_connection(conn)
                
                # Update stats
                execution_time = time.time() - start_time
                self._session_stats["commands_executed"] += 1
                
                # Check for errors in response
                if not response.get("success", True):
                    error_code = response.get("error_code", "COMMAND_FAILED")
                    error_message = response.get("error", "Unknown error")
                    
                    self._session_stats["errors_occurred"] += 1
                    
                    return CommandResult(
                        success=False,
                        data={},
                        error_code=error_code,
                        error_message=error_message,
                        execution_time=execution_time
                    )
                
                return CommandResult(
                    success=True,
                    data=response,
                    execution_time=execution_time
                )
                
            except Exception as e:
                # Return connection to pool even on error
                try:
                    await self.pool.return_connection(conn)
                except:
                    pass
                raise e
                
        except asyncio.TimeoutError:
            self._session_stats["errors_occurred"] += 1
            raise CommandError(
                f"Command timeout after {self.command_timeout}s",
                "COMMAND_TIMEOUT",
                {"command": command.get("action", "unknown")}
            )
        except Exception as e:
            self._session_stats["errors_occurred"] += 1
            raise CommandError(f"Command execution failed: {e}", "COMMAND_FAILED")
    
    async def move_to(self, 
                     target: Union[Tuple[int, int], str], 
                     profile: MotionProfile = MotionProfiles.NATURAL) -> CommandResult:
        """Move mouse to target location with human-like motion"""
        
        if isinstance(target, str):
            # Template matching
            target_coords = await self._find_target_image(target)
            if not target_coords:
                raise VisionError(f"Could not find target image: {target}", "TARGET_NOT_FOUND")
        else:
            target_coords = target
        
        command = {
            "action": "move_to",
            "x": target_coords[0],
            "y": target_coords[1],
            "profile": asdict(profile)
        }
        
        result = await self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Move failed: {result.error_message}",
                result.error_code,
                {"target": target_coords, "profile": profile.name}
            )
        
        return result
    
    async def click(self, 
                   button: str = "left", 
                   duration: float = 0.05) -> CommandResult:
        """Perform a mouse click with human-like timing"""
        command = {
            "action": "click",
            "button": button,
            "duration": duration
        }
        
        result = await self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Click failed: {result.error_message}",
                result.error_code,
                {"button": button, "duration": duration}
            )
        
        return result
    
    async def type_text(self, 
                       text: str, 
                       profile: str = "average") -> CommandResult:
        """Type text with human-like rhythm and timing"""
        command = {
            "action": "type",
            "text": text,
            "profile": profile
        }
        
        result = await self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Type failed: {result.error_message}",
                result.error_code,
                {"text_length": len(text), "profile": profile}
            )
        
        return result
    
    async def _find_target_image(self, image_path: str) -> Optional[Tuple[int, int]]:
        """Find target image on screen using enhanced vision system"""
        try:
            # Load template from cache
            template = self.vision_cache.get_template(image_path)
            if template is None:
                raise VisionError(f"Could not load template: {image_path}", "TEMPLATE_LOAD_FAILED")
            
            # Get screenshot
            screenshot_result = await self._send_command({"action": "screenshot"})
            if not screenshot_result.success:
                raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
            
            # Decode screenshot
            image_data = base64.b64decode(screenshot_result.data["image"])
            screenshot = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Use enhanced matching with fallbacks
            match = self.matcher.find_template_with_fallbacks(screenshot, template, confidence=0.7)
            
            if match:
                return (match.center_x, match.center_y)
            
            # Try multi-monitor search
            matches = self.multi_monitor.find_template_all_monitors(template, confidence=0.7)
            if matches:
                return (matches[0].center_x, matches[0].center_y)
            
            return None
            
        except Exception as e:
            raise VisionError(f"Vision search failed: {e}", "VISION_SEARCH_FAILED")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        duration = time.time() - self._session_stats["session_start"]
        return {
            **self._session_stats,
            "session_duration": duration,
            "session_id": self._session_id,
            "commands_per_second": self._session_stats["commands_executed"] / max(duration, 1)
        }


# Async context manager for easy usage
@asynccontextmanager
async def async_automation_session(**kwargs):
    """Async context manager for automation sessions"""
    async with AsyncHumanMouse(**kwargs) as bot:
        yield bot


# Backwards compatibility aliases
AsyncBrowserGeist = AsyncHumanMouse
