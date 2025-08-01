"""
BrowserGeist Python SDK

Provides a clean, ergonomic interface for human-like browser automation
using the underlying HID driver and motion engine.
"""

import socket
import json
import time
import cv2
import numpy as np
import base64
from typing import Optional, Tuple, Union, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import sys
import os
import logging
from contextlib import contextmanager

# Add vision module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vision'))
from template_matcher import TemplateMatcher, MatchResult, VisionCache

# Import CAPTCHA solver and wait system
try:
    from .captcha_solver import CaptchaSolver, CaptchaSolveMethod, CaptchaSolution
    from .user_personas import UserPersona, get_persona, list_personas, PERSONAS
    from .wait_conditions import WaitSystem, ExpectationSystem, WaitTimeoutError
except ImportError:
    # Fallback for when module is imported directly
    from captcha_solver import CaptchaSolver, CaptchaSolveMethod, CaptchaSolution
    from user_personas import UserPersona, get_persona, list_personas, PERSONAS
    from wait_conditions import WaitSystem, ExpectationSystem, WaitTimeoutError


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


@dataclass
class MotionProfile:
    """Motion profile for human-like movement"""
    name: str
    max_velocity: float
    acceleration: float
    jitter_amount: float
    overshoot_chance: float
    dwell_time_min: float
    dwell_time_max: float


class MotionProfiles:
    NATURAL = MotionProfile("natural", 800.0, 2000.0, 2.0, 0.15, 0.02, 0.08)
    CAREFUL = MotionProfile("careful", 400.0, 1200.0, 1.0, 0.05, 0.05, 0.12)
    FAST = MotionProfile("fast", 1200.0, 3000.0, 3.0, 0.25, 0.01, 0.04)


class HumanMouse:
    """Main interface for human-like mouse automation"""
    
    def __init__(self, 
                 daemon_socket: str = "/tmp/browsergeist.sock",
                 openai_api_key: Optional[str] = None,
                 twocaptcha_api_key: Optional[str] = None,
                 auto_solve_captcha: bool = True,
                 command_timeout: float = 30.0,
                 persona: Union[str, UserPersona, None] = None):
        """
        Initialize HumanMouse instance
        
        Args:
            daemon_socket: Path to daemon socket
            openai_api_key: OpenAI API key for CAPTCHA solving
            twocaptcha_api_key: 2Captcha API key for CAPTCHA solving
            auto_solve_captcha: Enable automatic CAPTCHA detection/solving
            command_timeout: Timeout for command execution
            persona: User persona name or UserPersona object for realistic behavior
        """
        self.daemon_socket = daemon_socket
        self.command_timeout = command_timeout
        self.socket = None
        self.matcher = TemplateMatcher()
        self.vision_cache = VisionCache()
        self.auto_solve_captcha = auto_solve_captcha
        
        # Initialize persona
        self.persona = self._initialize_persona(persona)
        
        # Initialize CAPTCHA solver
        self.captcha_solver = CaptchaSolver(
            openai_api_key=openai_api_key,
            twocaptcha_api_key=twocaptcha_api_key
        ) if (openai_api_key or twocaptcha_api_key or auto_solve_captcha) else None
        
        # Session state
        self._session_stats = {
            "commands_executed": 0,
            "errors_occurred": 0,
            "session_start": time.time()
        }
        
        # Logging
        self.logger = logging.getLogger("browsergeist")
        
        # Initialize wait system and expectations
        self.wait = WaitSystem(self)
        self.expect = ExpectationSystem(self.wait)
        
        self._connect()
    
    def _initialize_persona(self, persona: Union[str, UserPersona, None]) -> Optional[UserPersona]:
        """Initialize user persona from name or object"""
        if persona is None:
            return None
        elif isinstance(persona, str):
            try:
                return get_persona(persona)
            except ValueError as e:
                raise ValueError(f"Invalid persona name: {persona}. Available: {list_personas()}")
        elif isinstance(persona, UserPersona):
            return persona
        else:
            raise TypeError(f"Persona must be string or UserPersona, got {type(persona)}")
    
    def set_persona(self, persona: Union[str, UserPersona]) -> None:
        """Change the current persona"""
        self.persona = self._initialize_persona(persona)
        if self.persona:
            self.logger.info(f"Switched to persona: {self.persona.name}")
    
    def get_current_persona(self) -> Optional[Dict[str, Any]]:
        """Get current persona information"""
        if not self.persona:
            return None
        
        return {
            "name": self.persona.name,
            "description": self.persona.description,
            "experience_level": self.persona.experience_level.value,
            "current_energy": self.persona.current_energy_level,
            "current_focus": self.persona.current_focus_level,
            "fatigue": self.persona.fatigue_accumulation
        }
    
    def update_persona_state(self) -> None:
        """Update persona state (energy, focus, fatigue)"""
        if self.persona:
            session_duration = time.time() - self._session_stats["session_start"]
            self.persona.accumulate_fatigue(session_duration / 60.0)
            self.persona.update_session_state()
    
    def _adapt_motion_profile_for_persona(self, base_profile: MotionProfile) -> MotionProfile:
        """Adapt motion profile based on current persona characteristics"""
        if not self.persona:
            return base_profile
        
        mouse_behavior = self.persona.mouse_behavior
        
        # Get persona-adjusted values
        adjusted_speed = mouse_behavior.base_speed
        adjusted_precision = mouse_behavior.precision_level
        
        # Create new profile with persona characteristics
        return MotionProfile(
            name=f"{base_profile.name}_persona_{self.persona.name.lower().replace(' ', '_')}",
            max_velocity=adjusted_speed,
            acceleration=adjusted_speed * 2.5,  # Proportional acceleration
            jitter_amount=2.0 * (1.0 - adjusted_precision),  # More jitter for less precise users
            overshoot_chance=mouse_behavior.overshoot_tendency,
            dwell_time_min=mouse_behavior.dwell_time_ms[0] / 1000.0,  # Convert to seconds
            dwell_time_max=mouse_behavior.dwell_time_ms[1] / 1000.0
        )
    
    def _adapt_typing_for_persona(self, text: str, base_profile: str = "average") -> Dict[str, Any]:
        """Adapt typing behavior based on persona characteristics"""
        if not self.persona:
            return {"profile": base_profile, "text": text}
        
        kb_behavior = self.persona.keyboard_behavior
        
        # Calculate persona-adjusted typing speed
        adjusted_wpm = self.persona.get_adjusted_typing_speed()
        
        # Determine typing profile based on persona
        if kb_behavior.typing_style.value == "touch_typing":
            typing_profile = "fast"
        elif kb_behavior.typing_style.value == "hunt_and_peck":
            typing_profile = "careful"
        else:
            typing_profile = "average"
        
        return {
            "profile": typing_profile,
            "text": text,
            "persona_wpm": adjusted_wpm,
            "error_rate": kb_behavior.error_rate,
            "thinking_pause_chance": kb_behavior.thinking_pause_chance
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def close(self):
        """Close connection and cleanup resources"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        duration = time.time() - self._session_stats["session_start"]
        self.logger.info(f"Session closed after {duration:.2f}s")
        self.logger.info(f"Session stats: {self._session_stats}")
        
        self.vision_cache.clear()
        
    def _connect(self):
        """Connect to the control daemon"""
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.settimeout(self.command_timeout)
            self.socket.connect(self.daemon_socket)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to daemon: {e}", "CONNECTION_FAILED")
    
    def _send_command(self, command: Dict[str, Any]) -> CommandResult:
        """Send command to daemon with enhanced error handling"""
        start_time = time.time()
        
        try:
            # Ensure connection
            if not self.socket:
                self._connect()
            
            # Send command
            message = json.dumps(command).encode('utf-8')
            self.socket.send(len(message).to_bytes(4, 'big') + message)
            
            # Read response
            length = int.from_bytes(self.socket.recv(4), 'big')
            response = self.socket.recv(length).decode('utf-8')
            response_data = json.loads(response)
            
            # Update stats
            execution_time = time.time() - start_time
            self._session_stats["commands_executed"] += 1
            
            # Check for errors in response
            if not response_data.get("success", True):
                error_code = response_data.get("error_code", "COMMAND_FAILED")
                error_message = response_data.get("error", "Unknown error")
                
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
                data=response_data,
                execution_time=execution_time
            )
            
        except socket.timeout:
            self._session_stats["errors_occurred"] += 1
            raise CommandError(
                f"Command timeout after {self.command_timeout}s",
                "COMMAND_TIMEOUT",
                {"command": command.get("action", "unknown")}
            )
        except Exception as e:
            self._session_stats["errors_occurred"] += 1
            # Try to reconnect on connection error
            if "broken pipe" in str(e).lower() or "connection" in str(e).lower():
                self.socket = None
                raise ConnectionError(f"Connection lost: {e}", "CONNECTION_LOST")
            else:
                raise CommandError(f"Command execution failed: {e}", "COMMAND_FAILED")
    
    def move_to(self, 
                target: Union[Tuple[int, int], str], 
                profile: MotionProfile = MotionProfiles.NATURAL,
                use_persona: bool = True) -> CommandResult:
        """Move mouse to target location with human-like motion"""
        
        # Update persona state if using persona
        if use_persona and self.persona:
            self.update_persona_state()
        
        if isinstance(target, str):
            # Template matching
            target_coords = self._find_target_image(target)
            if not target_coords:
                raise VisionError(f"Could not find target image: {target}", "TARGET_NOT_FOUND")
        else:
            target_coords = target
        
        # Adapt profile based on persona if available
        if use_persona and self.persona:
            profile = self._adapt_motion_profile_for_persona(profile)
            
        command = {
            "action": "move_to",
            "x": target_coords[0],
            "y": target_coords[1],
            "profile": {
                "name": profile.name,
                "max_velocity": profile.max_velocity,
                "acceleration": profile.acceleration,
                "jitter_amount": profile.jitter_amount,
                "overshoot_chance": profile.overshoot_chance,
                "dwell_time_min": profile.dwell_time_min,
                "dwell_time_max": profile.dwell_time_max
            },
            "persona": self.persona.name if self.persona else None
        }
        
        result = self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Move failed: {result.error_message}",
                result.error_code,
                {"target": target_coords, "profile": profile.name, "persona": self.persona.name if self.persona else None}
            )
        
        return result
    
    def click(self, 
              button: str = "left", 
              duration: float = 0.05) -> CommandResult:
        """Perform a mouse click with human-like timing"""
        command = {
            "action": "click",
            "button": button,
            "duration": duration
        }
        
        result = self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Click failed: {result.error_message}",
                result.error_code,
                {"button": button, "duration": duration}
            )
        
        return result
    
    def type_text(self, 
                  text: str, 
                  delay_profile: str = "average",
                  use_persona: bool = True) -> CommandResult:
        """Type text with human-like rhythm and timing"""
        
        # Update persona state if using persona
        if use_persona and self.persona:
            self.update_persona_state()
            typing_params = self._adapt_typing_for_persona(text, delay_profile)
        else:
            typing_params = {"profile": delay_profile, "text": text}
        
        command = {
            "action": "type",
            "text": typing_params["text"],
            "profile": typing_params["profile"],
            "persona": self.persona.name if self.persona else None,
            "persona_params": typing_params if use_persona and self.persona else None
        }
        
        result = self._send_command(command)
        if not result.success:
            raise CommandError(
                f"Type failed: {result.error_message}",
                result.error_code,
                {"text_length": len(text), "profile": typing_params["profile"], "persona": self.persona.name if self.persona else None}
            )
        
        return result
    
    def type(self, text: str, delay_profile: str = "average"):
        """Type text with human-like delays between keystrokes"""
        command = {
            "action": "type",
            "text": text,
            "delay_profile": delay_profile
        }
        
        result = self._send_command(command)
        if not result.success:
            raise CommandError(f"Type failed: {result.error_message}", result.error_code)
    
    def scroll(self, dx: int = 0, dy: int = 0, smooth: bool = True):
        """Scroll with human-like motion"""
        command = {
            "action": "scroll",
            "dx": dx,
            "dy": dy,
            "smooth": smooth
        }
        
        result = self._send_command(command)
        if not result.success:
            raise CommandError(f"Scroll failed: {result.error_message}", result.error_code)
    
    def _find_target_image(self, image_path: str, 
                          confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find target image on screen using advanced template matching"""
        # Take screenshot
        screenshot_command = {"action": "screenshot"}
        screenshot_response = self._send_command(screenshot_command)
        
        if not screenshot_response.get("success"):
            return None
        
        # Decode base64 screenshot data
        screenshot_data = base64.b64decode(screenshot_response["data"])
        screenshot_array = np.frombuffer(screenshot_data, dtype=np.uint8)
        screenshot = cv2.imdecode(screenshot_array, cv2.IMREAD_COLOR)
        
        if screenshot is None:
            return None
        
        # Load template from cache or file
        template = self.vision_cache.get_template(image_path)
        if template is None:
            return None
        
        # Use advanced template matching
        match_result = self.matcher.find_template(
            screenshot, template, confidence=confidence, method="auto"
        )
        
        if match_result:
            return match_result.center
        
        return None
    
    def check_for_captcha(self, methods: Optional[List[CaptchaSolveMethod]] = None) -> Optional[CaptchaSolution]:
        """
        Check current screen for CAPTCHA and solve if found
        
        Args:
            methods: List of solving methods to try in order
            
        Returns:
            CaptchaSolution if CAPTCHA found and solved, None if no CAPTCHA
        """
        if not self.captcha_solver:
            print("⚠️ CAPTCHA solver not initialized. Provide API keys or enable auto_solve_captcha")
            return None
            
        # Get current screenshot
        screenshot = self._get_screenshot()
        if screenshot is None:
            return None
            
        # Detect and solve CAPTCHA
        return self.captcha_solver.detect_and_solve(screenshot, methods)
    
    def solve_captcha_if_present(self, methods: Optional[List[CaptchaSolveMethod]] = None) -> bool:
        """
        Check for CAPTCHA and solve it if present, then continue automation
        
        Args:
            methods: List of solving methods to try in order
            
        Returns:
            True if no CAPTCHA or CAPTCHA solved successfully, False if failed
        """
        solution = self.check_for_captcha(methods)
        
        if solution is None:
            # No CAPTCHA detected
            return True
        
        if not solution.success:
            print(f"❌ Failed to solve CAPTCHA: {solution.error}")
            return False
        
        # Execute solution
        return self._execute_captcha_solution(solution)
    
    def _execute_captcha_solution(self, solution: CaptchaSolution) -> bool:
        """Execute the CAPTCHA solution (type text or click coordinates)"""
        try:
            if solution.solution:
                # Text-based CAPTCHA solution
                print(f"📝 Typing CAPTCHA solution: {solution.solution}")
                self.type(solution.solution)
                return True
                
            elif solution.coordinates:
                # Coordinate-based CAPTCHA solution (image selection)
                print(f"🎯 Clicking CAPTCHA coordinates: {solution.coordinates}")
                for x, y in solution.coordinates:
                    self.move_to((x, y))
                    self.click()
                    time.sleep(0.5)  # Small delay between clicks
                return True
                
            else:
                print("⚠️ CAPTCHA solution format not recognized")
                return False
                
        except Exception as e:
            print(f"❌ Error executing CAPTCHA solution: {e}")
            return False
    
    def _get_screenshot(self) -> Optional[np.ndarray]:
        """Get current screenshot from daemon"""
        try:
            response = self._send_command({"action": "screenshot"})
            
            if response.get("success"):
                # Decode base64 image
                image_data = base64.b64decode(response["image"])
                nparr = np.frombuffer(image_data, np.uint8)
                screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return screenshot
            else:
                print(f"Failed to get screenshot: {response.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error getting screenshot: {e}")
            return None
    
    def auto_handle_captcha(self, action_func, *args, **kwargs):
        """
        Decorator-like method to automatically handle CAPTCHAs during actions
        
        Args:
            action_func: Function to execute that might encounter CAPTCHA
            *args, **kwargs: Arguments for the action function
            
        Returns:
            Result of action_func, handling any CAPTCHAs encountered
        """
        if not self.auto_solve_captcha:
            return action_func(*args, **kwargs)
        
        # Execute action
        try:
            result = action_func(*args, **kwargs)
            
            # Check for CAPTCHA after action
            time.sleep(1)  # Give page time to load
            captcha_solved = self.solve_captcha_if_present()
            
            if not captcha_solved:
                print("⚠️ Action may have failed due to unsolved CAPTCHA")
            
            return result
            
        except Exception as e:
            # Check if failure might be due to CAPTCHA
            print(f"Action failed: {e}. Checking for CAPTCHA...")
            captcha_solved = self.solve_captcha_if_present()
            
            if captcha_solved:
                print("🔄 Retrying action after solving CAPTCHA...")
                return action_func(*args, **kwargs)
            else:
                raise e
    
    def click_with_captcha_handling(self, button: int = 1):
        """Click with automatic CAPTCHA handling"""
        return self.auto_handle_captcha(self.click, button)
    
    def type_with_captcha_handling(self, text: str, delay_profile: str = "average"):
        """Type with automatic CAPTCHA handling"""
        return self.auto_handle_captcha(self.type, text, delay_profile)
    
    def move_to_with_captcha_handling(self, target: Union[Tuple[int, int], str], 
                                    profile: MotionProfile = MotionProfiles.NATURAL):
        """Move to target with automatic CAPTCHA handling"""
        return self.auto_handle_captcha(self.move_to, target, profile)
    
    # ===== Natural Element Targeting API =====
    
    def click_text(self, text: str, confidence: float = 0.8, 
                   button: str = "left", duration: float = 0.05,
                   use_persona: bool = True, use_accessibility: bool = True,
                   fuzzy_threshold: float = 0.6) -> CommandResult:
        """Click on text found via OCR or Accessibility API
        
        Args:
            text: Text to search for and click
            confidence: OCR confidence threshold (0.0-1.0)
            button: Mouse button ("left", "right", "middle")
            duration: Click duration in seconds
            use_persona: Whether to use persona for motion adaptation
            use_accessibility: Whether to try accessibility API first
            fuzzy_threshold: Fuzzy matching threshold for OCR (0.0-1.0)
            
        Returns:
            CommandResult with success status and details
        """
        target_coords = None
        method_used = "unknown"
        
        # Try accessibility API first if enabled
        if use_accessibility:
            try:
                command = {"action": "find_element_by_text", "text": text}
                result = self._send_command(command)
                if result.success and "x" in result.details and "y" in result.details:
                    target_coords = (result.details["x"], result.details["y"])
                    method_used = "accessibility"
            except Exception as e:
                # Fall back to OCR
                pass
        
        # Fall back to OCR if accessibility didn't work
        if not target_coords:
            # Take screenshot and find text
            screenshot = self._take_screenshot()
            if not screenshot:
                raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
            
            # Use OCR to find text with fuzzy matching
            ocr_result = self.vision.find_text(screenshot, text, confidence, fuzzy_threshold)
            if ocr_result:
                target_coords = ocr_result.center
                method_used = "ocr"
        
        if not target_coords:
            raise VisionError(f"Text '{text}' not found", "TEXT_NOT_FOUND", {"text": text, "confidence": confidence, "methods_tried": ["accessibility", "ocr"] if use_accessibility else ["ocr"]})
        
        # Move to text and click
        self.move_to(target_coords, use_persona=use_persona)
        click_result = self.click(button, duration)
        click_result.details["targeting_method"] = method_used
        return click_result
    
    def click_button(self, button_text: Optional[str] = None, 
                     button_image: Optional[str] = None,
                     confidence: float = 0.8,
                     use_persona: bool = True) -> CommandResult:
        """Click on a button by text or image
        
        Args:
            button_text: Text on the button (e.g., "Submit", "Login", "OK")
            button_image: Path to button template image
            confidence: Matching confidence threshold
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details
        """
        if button_text:
            return self.click_text(button_text, confidence, use_persona=use_persona)
        elif button_image:
            return self.click_image(button_image, confidence, use_persona=use_persona)
        else:
            raise ValueError("Either button_text or button_image must be provided")
    
    def click_link(self, link_text: str, confidence: float = 0.8,
                   use_persona: bool = True) -> CommandResult:
        """Click on a link by its text
        
        Args:
            link_text: Text of the link to click
            confidence: OCR confidence threshold
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details
        """
        return self.click_text(link_text, confidence, use_persona=use_persona)
    
    def click_image(self, image_path: str, confidence: float = 0.8,
                    use_persona: bool = True) -> CommandResult:
        """Click on an image/UI element by template matching
        
        Args:
            image_path: Path to template image
            confidence: Template matching confidence threshold
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details
        """
        # Take screenshot
        screenshot = self._take_screenshot()
        if not screenshot:
            raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
        
        # Find template with fallbacks for robustness
        result = self.vision.find_template_with_fallbacks(screenshot, image_path, confidence)
        if not result:
            raise VisionError(f"Image '{image_path}' not found", "IMAGE_NOT_FOUND", {"image": image_path, "confidence": confidence})
        
        # Move to image and click
        self.move_to(result.center, use_persona=use_persona)
        return self.click()
    
    def type_in_field(self, field_text: str, content: str, 
                      confidence: float = 0.8,
                      delay_profile: str = "average",
                      clear_field: bool = True,
                      use_persona: bool = True,
                      use_accessibility: bool = True) -> CommandResult:
        """Type content into a form field identified by label text
        
        Args:
            field_text: Text label near the field (e.g., "Email", "Password", "Name")
            content: Text content to type
            confidence: OCR confidence for finding field
            delay_profile: Typing speed profile
            clear_field: Whether to clear field before typing
            use_persona: Whether to use persona for motion adaptation
            use_accessibility: Whether to try accessibility API first
            
        Returns:
            CommandResult with success status and details
        """
        input_field = None
        method_used = "unknown"
        
        # Try accessibility API first if enabled
        if use_accessibility:
            try:
                command = {"action": "find_input_field", "label": field_text}
                result = self._send_command(command)
                if result.success and "x" in result.details and "y" in result.details:
                    input_field = (result.details["x"], result.details["y"])
                    method_used = "accessibility"
            except Exception:
                # Fall back to OCR
                pass
        
        # Fall back to OCR-based field detection if accessibility didn't work
        if not input_field:
            # Find the field label
            screenshot = self._take_screenshot()
            if not screenshot:
                raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
            
            field_result = self.vision.find_text(screenshot, field_text, confidence)
            if not field_result:
                raise VisionError(f"Field '{field_text}' not found", "FIELD_NOT_FOUND", {"field": field_text, "confidence": confidence})
            
            # Look for input field near the label (typically to the right or below)
            input_field = self._find_input_field_near(screenshot, field_result)
            if not input_field:
                # Fallback: click near the label text
                click_x = field_result.center_x + field_result.width + 20  # Try to the right
                click_y = field_result.center_y
                input_field = (click_x, click_y)
            method_used = "ocr"
        
        if not input_field:
            raise VisionError(f"Input field for '{field_text}' not found", "INPUT_FIELD_NOT_FOUND", {"field": field_text})
        
        # Click on input field
        self.move_to(input_field, use_persona=use_persona)
        self.click()
        
        # Clear field if requested
        if clear_field:
            self._send_command({"action": "key_combination", "keys": ["cmd", "a"]})  # Select all
            time.sleep(0.1)
        
        # Type content
        type_result = self.type_text(content, delay_profile, use_persona)
        type_result.details["targeting_method"] = method_used
        return type_result
    
    def find_and_click_any(self, candidates: List[str], 
                          confidence: float = 0.8,
                          use_persona: bool = True) -> CommandResult:
        """Find and click the first available element from a list of candidates
        
        Args:
            candidates: List of text strings or image paths to search for
            confidence: Matching confidence threshold
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details about which candidate was found
        """
        screenshot = self._take_screenshot()
        if not screenshot:
            raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
        
        for candidate in candidates:
            try:
                if candidate.endswith(('.png', '.jpg', '.jpeg')):
                    # Image template
                    result = self.vision.find_template_with_fallbacks(screenshot, candidate, confidence)
                else:
                    # Text search
                    result = self.vision.find_text(screenshot, candidate, confidence)
                
                if result:
                    self.move_to(result.center, use_persona=use_persona)
                    click_result = self.click()
                    click_result.details = {"found_candidate": candidate, "method": "text" if not candidate.endswith(('.png', '.jpg', '.jpeg')) else "image"}
                    return click_result
                    
            except Exception as e:
                # Continue searching other candidates
                continue
        
        raise VisionError("None of the candidates found", "NO_CANDIDATES_FOUND", {"candidates": candidates})
    
    def _find_input_field_near(self, screenshot, label_result) -> Optional[Tuple[int, int]]:
        """Find input field near a label using heuristics and vision"""
        # Try common input field patterns near the label
        search_areas = [
            # To the right of label
            (label_result.center_x + label_result.width + 10, label_result.center_y),
            (label_result.center_x + label_result.width + 30, label_result.center_y),
            # Below label
            (label_result.center_x, label_result.center_y + 30),
            (label_result.center_x, label_result.center_y + 50),
            # Above label (less common)
            (label_result.center_x, label_result.center_y - 30),
        ]
        
        # For now, return first search area
        # TODO: Implement actual input field detection using image processing
        return search_areas[0] if search_areas else None
    
    def _take_screenshot(self):
        """Take a screenshot for vision operations"""
        try:
            command = {"action": "screenshot"}
            result = self._send_command(command)
            if result.success and "screenshot" in result.details:
                # Decode base64 screenshot
                import base64
                screenshot_data = base64.b64decode(result.details["screenshot"])
                nparr = np.frombuffer(screenshot_data, np.uint8)
                screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return screenshot
            else:
                return None
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        duration = time.time() - self._session_stats["session_start"]
        return {
            **self._session_stats,
            "session_duration": duration,
            "commands_per_second": self._session_stats["commands_executed"] / max(duration, 1)
        }
    
    # Safe interaction methods with automatic waiting
    
    def safe_click_text(self, text: str, 
                       timeout: Optional[float] = None,
                       confidence: float = 0.8,
                       button: str = "left",
                       duration: float = 0.05,
                       use_persona: bool = True,
                       use_accessibility: bool = True) -> CommandResult:
        """Safely click text after waiting for it to be visible
        
        Args:
            text: Text to find and click
            timeout: Maximum time to wait for element (uses default if None)
            confidence: Text recognition confidence threshold
            button: Mouse button to click
            duration: Click duration
            use_persona: Whether to use persona for motion adaptation
            use_accessibility: Whether to try accessibility API first
            
        Returns:
            CommandResult with success status and details
            
        Raises:
            WaitTimeoutError: If element is not found within timeout
        """
        # Wait for element to be visible
        coords = self.expect.element_to_be_visible(text, timeout, confidence, use_accessibility)
        
        # Move and click
        self.move_to(coords, use_persona=use_persona)
        click_result = self.click(button, duration)
        click_result.details["text"] = text
        click_result.details["wait_used"] = True
        return click_result
    
    def safe_click_image(self, image_path: str,
                        timeout: Optional[float] = None,
                        confidence: float = 0.8,
                        button: str = "left", 
                        duration: float = 0.05,
                        use_persona: bool = True) -> CommandResult:
        """Safely click image after waiting for it to be visible
        
        Args:
            image_path: Path to template image
            timeout: Maximum time to wait for element
            confidence: Template matching confidence threshold
            button: Mouse button to click
            duration: Click duration
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details
            
        Raises:
            WaitTimeoutError: If element is not found within timeout
        """
        # Wait for image to be visible
        result = self.wait.for_image(image_path, timeout, confidence)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError(f"Image '{image_path}' to be visible",
                                     timeout or self.wait.default_timeout,
                                     result.attempts)
            else:
                raise VisionError(f"Failed to find image '{image_path}': {result.error}")
        
        # Move and click
        self.move_to(result.value.center, use_persona=use_persona)
        click_result = self.click(button, duration)
        click_result.details["image_path"] = image_path
        click_result.details["wait_used"] = True
        return click_result
    
    def click_near_text(self, target_text: str, nearby_text: str,
                       confidence: float = 0.8, max_distance: float = 200.0,
                       button: str = "left", duration: float = 0.05,
                       use_persona: bool = True) -> CommandResult:
        """Click on element near specific text (context-aware targeting)
        
        Args:
            target_text: Primary text to look for
            nearby_text: Text that should be near the target
            confidence: OCR confidence threshold
            max_distance: Maximum pixel distance between target and nearby text
            button: Mouse button to click
            duration: Click duration
            use_persona: Whether to use persona for motion adaptation
            
        Returns:
            CommandResult with success status and details
        """
        # Take screenshot
        screenshot = self._take_screenshot()
        if not screenshot:
            raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
        
        # Find all text occurrences using OCR
        try:
            import pytesseract
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Get all text data with positions
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            
            # Find target and nearby text positions
            target_positions = []
            nearby_positions = []
            
            for i, text in enumerate(data['text']):
                if not text or not text.strip():
                    continue
                    
                text_clean = text.strip().lower()
                ocr_confidence = float(data['conf'][i]) / 100.0
                
                if ocr_confidence < confidence:
                    continue
                
                # Check for target text
                if target_text.lower() in text_clean:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    target_positions.append((x, y, text, ocr_confidence))
                
                # Check for nearby text
                if nearby_text.lower() in text_clean:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    nearby_positions.append((x, y, text, ocr_confidence))
            
            # Find best target based on proximity to nearby text
            best_target = None
            best_score = 0.0
            
            for target_x, target_y, target_found, target_conf in target_positions:
                for nearby_x, nearby_y, nearby_found, nearby_conf in nearby_positions:
                    # Calculate distance
                    distance = ((target_x - nearby_x) ** 2 + (target_y - nearby_y) ** 2) ** 0.5
                    
                    if distance <= max_distance:
                        # Score based on confidence and proximity
                        proximity_score = 1.0 - (distance / max_distance)
                        combined_score = (target_conf + nearby_conf) / 2.0 * proximity_score
                        
                        if combined_score > best_score:
                            best_score = combined_score
                            best_target = (target_x, target_y)
            
            if best_target:
                # Move to target and click
                self.move_to(best_target, use_persona=use_persona)
                click_result = self.click(button, duration)
                click_result.details["targeting_method"] = "context_aware"
                click_result.details["context_score"] = best_score
                return click_result
            else:
                raise VisionError(f"Target '{target_text}' not found near '{nearby_text}'", 
                                "CONTEXT_NOT_FOUND", 
                                {"target_text": target_text, "nearby_text": nearby_text, "max_distance": max_distance})
                
        except ImportError:
            raise VisionError("pytesseract not installed", "OCR_UNAVAILABLE")
        except Exception as e:
            raise VisionError(f"Context-aware targeting failed: {e}", "CONTEXT_ERROR")

    def safe_type_in_field(self, field_text: str, content: str,
                          timeout: Optional[float] = None,
                          confidence: float = 0.8,
                          delay_profile: str = "average",
                          clear_field: bool = True,
                          use_persona: bool = True,
                          use_accessibility: bool = True) -> CommandResult:
        """Safely type in field after waiting for it to be visible
        
        Args:
            field_text: Text label of the field to find
            content: Text to type
            timeout: Maximum time to wait for field
            confidence: Text recognition confidence threshold
            delay_profile: Typing speed profile
            clear_field: Whether to clear field before typing
            use_persona: Whether to use persona for motion adaptation
            use_accessibility: Whether to try accessibility API first
            
        Returns:
            CommandResult with success status and details
            
        Raises:
            WaitTimeoutError: If field is not found within timeout
        """
        # Wait for field label to be visible
        coords = self.expect.element_to_be_visible(field_text, timeout, confidence, use_accessibility)
        
        # Find input field near the label
        screenshot = self._take_screenshot()
        if not screenshot:
            raise VisionError("Failed to capture screenshot", "SCREENSHOT_FAILED")
        
        # For now, use simple heuristic to find input field
        # TODO: Implement more sophisticated field detection
        input_field = self._find_input_field_near(screenshot, type('MockResult', (), {
            'center': coords,
            'center_x': coords[0],
            'center_y': coords[1], 
            'width': 100,
            'height': 20
        })())
        
        if not input_field:
            # Try clicking on the label itself as fallback
            input_field = coords
        
        # Click on input field
        self.move_to(input_field, use_persona=use_persona)
        self.click()
        
        # Clear field if requested
        if clear_field:
            self._send_command({"action": "key_combination", "keys": ["cmd", "a"]})
            time.sleep(0.1)
        
        # Type content
        type_result = self.type_text(content, delay_profile, use_persona)
        type_result.details["field_text"] = field_text
        type_result.details["wait_used"] = True
        return type_result
    
    def wait_for_page_load(self, timeout: Optional[float] = None,
                          stability_duration: float = 1.0,
                          similarity_threshold: float = 0.95) -> bool:
        """Wait for page to finish loading (screen to be stable)
        
        Args:
            timeout: Maximum time to wait
            stability_duration: How long screen must be stable
            similarity_threshold: Similarity threshold for stability detection
            
        Returns:
            True if page is stable, False if timeout
            
        Raises:
            WaitTimeoutError: If page doesn't stabilize within timeout
        """
        result = self.wait.for_stable_screen(timeout, stability_duration, similarity_threshold)
        if not result.success:
            if result.timeout:
                raise WaitTimeoutError("Page to finish loading",
                                     timeout or self.wait.default_timeout,
                                     result.attempts)
            else:
                raise Exception(f"Page stability check failed: {result.error}")
        return True
    
    def close(self):
        """Close connection to daemon"""
        if self.socket:
            self.socket.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def target(image_path: str) -> str:
    """Helper function for cleaner syntax when specifying image targets"""
    return image_path


@contextmanager
def automation_session(**kwargs):
    """Context manager for automation sessions"""
    with HumanMouse(**kwargs) as bot:
        yield bot


# Example usage
if __name__ == "__main__":
    with HumanMouse() as bot:
        # Find and click a button
        bot.move_to(target("login_button.png"))
        bot.click()
        
        # Type with human-like delays
        bot.type("user@example.com", delay_profile="careful")
        
        # Move to password field and enter password
        bot.move_to(target("password_field.png"))
        bot.click()
        bot.type("password123", delay_profile="average")
        
        # Submit form
        bot.move_to(target("submit_button.png"))
        bot.click()
