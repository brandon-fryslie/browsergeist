"""
BrowserGeist CAPTCHA Solving System

Provides three methods for CAPTCHA detection and solving:
1. OpenAI API integration for automated solving
2. Internal webserver for manual user solving 
3. 2Captcha API integration for outsourced solving
"""

import base64
import json
import threading
import time
import requests
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os
from pathlib import Path

class CaptchaSolveMethod(Enum):
    """Available CAPTCHA solving methods"""
    OPENAI = "openai"
    MANUAL = "manual" 
    TWOCAPTCHA = "2captcha"

@dataclass
class CaptchaChallenge:
    """Represents a detected CAPTCHA challenge"""
    image: np.ndarray
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    challenge_type: str
    confidence: float
    screenshot_path: Optional[str] = None

@dataclass
class CaptchaSolution:
    """Represents a CAPTCHA solution"""
    success: bool
    solution: Optional[str] = None
    coordinates: Optional[List[Tuple[int, int]]] = None
    method_used: Optional[CaptchaSolveMethod] = None
    error: Optional[str] = None

class CaptchaDetector:
    """Detects CAPTCHAs in screenshots using vision techniques"""
    
    def __init__(self):
        self.captcha_templates = self._load_captcha_templates()
        
    def _load_captcha_templates(self) -> Dict[str, np.ndarray]:
        """Load CAPTCHA template images for recognition"""
        templates = {}
        template_dir = Path(__file__).parent / "templates" / "captcha"
        
        if template_dir.exists():
            for template_file in template_dir.glob("*.png"):
                template = cv2.imread(str(template_file), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    templates[template_file.stem] = template
                    
        return templates
    
    def detect_captcha(self, screenshot: np.ndarray) -> Optional[CaptchaChallenge]:
        """
        Detect CAPTCHA in screenshot using multiple detection methods
        
        Args:
            screenshot: Screenshot as numpy array
            
        Returns:
            CaptchaChallenge if detected, None otherwise
        """
        
        # Validate input
        if screenshot.size == 0 or len(screenshot.shape) < 2:
            return None
            
        # Check minimum size requirements
        if screenshot.shape[0] < 10 or screenshot.shape[1] < 10:
            return None
        
        # Method 1: Template matching
        template_result = self._detect_by_template(screenshot)
        if template_result:
            return template_result
            
        # Method 2: Text-based detection
        text_result = self._detect_by_text(screenshot)
        if text_result:
            return text_result
            
        # Method 3: Visual pattern detection (with higher threshold to reduce false positives)
        pattern_result = self._detect_by_patterns(screenshot)
        if pattern_result:
            return pattern_result
            
        return None
    
    def _detect_by_template(self, screenshot: np.ndarray) -> Optional[CaptchaChallenge]:
        """Detect CAPTCHA using template matching"""
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        
        for template_name, template in self.captcha_templates.items():
            result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.7:  # High confidence threshold
                h, w = template.shape
                x, y = max_loc
                
                # Extract CAPTCHA region with some padding
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(screenshot.shape[1], x + w + padding)
                y2 = min(screenshot.shape[0], y + h + padding)
                
                captcha_region = screenshot[y1:y2, x1:x2]
                
                return CaptchaChallenge(
                    image=captcha_region,
                    bbox=(x1, y1, x2 - x1, y2 - y1),
                    challenge_type=template_name,
                    confidence=max_val
                )
                
        return None
    
    def _detect_by_text(self, screenshot: np.ndarray) -> Optional[CaptchaChallenge]:
        """Detect CAPTCHA by looking for common CAPTCHA text indicators"""
        try:
            import pytesseract
            
            # Convert to PIL Image for OCR
            if len(screenshot.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(screenshot)
                
            # Extract text
            text = pytesseract.image_to_string(pil_image).lower()
            
            # Common CAPTCHA indicators
            captcha_keywords = [
                "captcha", "verify", "human", "robot", "security",
                "prove", "verification", "challenge", "i'm not a robot",
                "select all", "click verify", "solve to continue"
            ]
            
            for keyword in captcha_keywords:
                if keyword in text:
                    # For text-based detection, return the whole screenshot region
                    return CaptchaChallenge(
                        image=screenshot,
                        bbox=(0, 0, screenshot.shape[1], screenshot.shape[0]),
                        challenge_type="text_based",
                        confidence=0.8
                    )
                    
        except Exception:
            # If OCR fails (e.g., empty image), return None
            pass
                
        return None
    
    def _detect_by_patterns(self, screenshot: np.ndarray) -> Optional[CaptchaChallenge]:
        """Detect CAPTCHA using visual patterns (grids, unusual UI elements)"""
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
        
        # Look for grid patterns (common in image selection CAPTCHAs)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        # Use higher threshold to reduce false positives
        if lines is not None and len(lines) > 20:
            # Check if lines form a regular grid pattern
            horizontal_lines = 0
            vertical_lines = 0
            
            for line in lines:
                rho, theta = line[0]
                if abs(theta) < 0.2 or abs(theta - np.pi) < 0.2:  # Horizontal lines
                    horizontal_lines += 1
                elif abs(theta - np.pi/2) < 0.2:  # Vertical lines
                    vertical_lines += 1
            
            # Require both horizontal and vertical lines for grid detection
            if horizontal_lines >= 3 and vertical_lines >= 3:
                return CaptchaChallenge(
                    image=screenshot,
                    bbox=(0, 0, screenshot.shape[1], screenshot.shape[0]),
                    challenge_type="grid_pattern",
                    confidence=0.6
                )
            
        return None

class OpenAICaptchaSolver:
    """Solves CAPTCHAs using OpenAI GPT-4 Vision API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """
        Solve CAPTCHA using OpenAI API
        
        Args:
            challenge: The CAPTCHA challenge to solve
            
        Returns:
            CaptchaSolution with result
        """
        try:
            # Convert image to base64
            image_b64 = self._image_to_base64(challenge.image)
            
            # Create prompt based on challenge type
            prompt = self._create_prompt(challenge)
            
            # Call OpenAI API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the response
            return self._parse_openai_response(content)
            
        except Exception as e:
            return CaptchaSolution(
                success=False,
                error=f"OpenAI API error: {str(e)}",
                method_used=CaptchaSolveMethod.OPENAI
            )
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert numpy image to base64 string"""
        # Convert to RGB if needed
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # Save to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        
        # Encode to base64
        return base64.b64encode(image_bytes).decode()
    
    def _create_prompt(self, challenge: CaptchaChallenge) -> str:
        """Create appropriate prompt for the CAPTCHA type"""
        base_prompt = """
You are a CAPTCHA solving assistant. Analyze this image and provide the solution.

Response format:
- For text CAPTCHAs: Return only the text/numbers shown
- For image selection CAPTCHAs: Return coordinates as JSON array like [{"x": 100, "y": 150}, {"x": 200, "y": 250}]
- For checkbox CAPTCHAs: Return "checkbox" to indicate clicking the checkbox
- If unsolvable: Return "UNSOLVABLE"

Important: Only return the solution, no explanation or additional text.
"""
        
        if challenge.challenge_type == "text_based":
            return base_prompt + "\nThis appears to be a text-based CAPTCHA. Please read and return the text/numbers shown."
        elif challenge.challenge_type == "grid_pattern":
            return base_prompt + "\nThis appears to be an image selection CAPTCHA. Return coordinates of items to click."
        else:
            return base_prompt + "\nPlease analyze this CAPTCHA and provide the appropriate solution."
    
    def _parse_openai_response(self, content: str) -> CaptchaSolution:
        """Parse OpenAI response into CaptchaSolution"""
        content = content.strip()
        
        if content == "UNSOLVABLE":
            return CaptchaSolution(
                success=False,
                error="OpenAI indicated CAPTCHA is unsolvable",
                method_used=CaptchaSolveMethod.OPENAI
            )
        
        # Try to parse as JSON (coordinates)
        try:
            coordinates = json.loads(content)
            if isinstance(coordinates, list):
                coord_list = [(coord["x"], coord["y"]) for coord in coordinates if "x" in coord and "y" in coord]
                return CaptchaSolution(
                    success=True,
                    coordinates=coord_list,
                    method_used=CaptchaSolveMethod.OPENAI
                )
        except json.JSONDecodeError:
            pass
        
        # Treat as text solution
        return CaptchaSolution(
            success=True,
            solution=content,
            method_used=CaptchaSolveMethod.OPENAI
        )

class ManualCaptchaSolver:
    """Provides manual CAPTCHA solving via internal webserver"""
    
    def __init__(self, port: int = 8899):
        self.port = port
        self.server_thread = None
        self.current_challenge = None
        self.solution_ready = threading.Event()
        self.solution = None
        
    def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """
        Solve CAPTCHA manually by starting webserver and waiting for user input
        
        Args:
            challenge: The CAPTCHA challenge to solve
            
        Returns:
            CaptchaSolution with user-provided result
        """
        try:
            # Save challenge image to temp file
            temp_image_path = self._save_challenge_image(challenge)
            
            # Start webserver if not running
            if not self.server_thread or not self.server_thread.is_alive():
                self._start_webserver()
            
            # Set current challenge
            self.current_challenge = {
                "image_path": temp_image_path,
                "challenge_type": challenge.challenge_type,
                "bbox": challenge.bbox
            }
            
            # Notify user
            print(f"\n🤖 CAPTCHA Detected!")
            print(f"Please solve the CAPTCHA at: http://localhost:{self.port}")
            print(f"Challenge type: {challenge.challenge_type}")
            print("Waiting for your solution...")
            
            # Wait for solution (with timeout)
            if self.solution_ready.wait(timeout=300):  # 5 minute timeout
                solution = self.solution
                self.solution = None
                self.solution_ready.clear()
                
                if solution:
                    return CaptchaSolution(
                        success=True,
                        solution=solution.get("text"),
                        coordinates=solution.get("coordinates"),
                        method_used=CaptchaSolveMethod.MANUAL
                    )
                else:
                    return CaptchaSolution(
                        success=False,
                        error="User cancelled CAPTCHA solving",
                        method_used=CaptchaSolveMethod.MANUAL
                    )
            else:
                return CaptchaSolution(
                    success=False,
                    error="Timeout waiting for user solution",
                    method_used=CaptchaSolveMethod.MANUAL
                )
                
        except Exception as e:
            return CaptchaSolution(
                success=False,
                error=f"Manual solving error: {str(e)}",
                method_used=CaptchaSolveMethod.MANUAL
            )
    
    def _save_challenge_image(self, challenge: CaptchaChallenge) -> str:
        """Save challenge image to temporary file"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"browsergeist_captcha_{int(time.time())}.png")
        
        # Convert and save image
        if len(challenge.image.shape) == 3:
            image_rgb = cv2.cvtColor(challenge.image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(challenge.image, cv2.COLOR_GRAY2RGB)
            
        pil_image = Image.fromarray(image_rgb)
        pil_image.save(temp_path)
        
        return temp_path
    
    def _start_webserver(self):
        """Start internal webserver for manual CAPTCHA solving"""
        try:
            from flask import Flask, render_template_string, request, jsonify
            
            app = Flask(__name__)
            
            @app.route('/')
            def index():
                if not self.current_challenge:
                    return "No CAPTCHA challenge available"
                
                # Simple HTML interface
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>BrowserGeist CAPTCHA Solver</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .challenge { border: 1px solid #ccc; padding: 20px; border-radius: 8px; }
                        .image { margin: 20px 0; }
                        .solution { margin: 20px 0; }
                        button { padding: 10px 20px; margin: 5px; }
                        input[type="text"] { padding: 8px; width: 300px; }
                    </style>
                </head>
                <body>
                    <h1>🤖 BrowserGeist CAPTCHA Solver</h1>
                    <div class="challenge">
                        <h2>CAPTCHA Challenge</h2>
                        <p><strong>Type:</strong> {{ challenge_type }}</p>
                        <div class="image">
                            <img src="/captcha_image" alt="CAPTCHA" style="max-width: 100%; border: 1px solid #ddd;">
                        </div>
                        <div class="solution">
                            <h3>Solution:</h3>
                            <input type="text" id="solution_text" placeholder="Enter text solution here...">
                            <br><br>
                            <button onclick="submitSolution()">Submit Solution</button>
                            <button onclick="skipCaptcha()">Skip/Cancel</button>
                        </div>
                    </div>
                    
                    <script>
                        function submitSolution() {
                            const text = document.getElementById('solution_text').value;
                            if (!text.trim()) {
                                alert('Please enter a solution');
                                return;
                            }
                            
                            fetch('/submit_solution', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({text: text})
                            }).then(response => {
                                if (response.ok) {
                                    document.body.innerHTML = '<h1>✅ Solution Submitted!</h1><p>You can close this window.</p>';
                                }
                            });
                        }
                        
                        function skipCaptcha() {
                            fetch('/skip', {method: 'POST'}).then(response => {
                                if (response.ok) {
                                    document.body.innerHTML = '<h1>❌ CAPTCHA Skipped</h1><p>You can close this window.</p>';
                                }
                            });
                        }
                    </script>
                </body>
                </html>
                """
                return render_template_string(html, challenge_type=self.current_challenge["challenge_type"])
            
            @app.route('/captcha_image')
            def captcha_image():
                if self.current_challenge and os.path.exists(self.current_challenge["image_path"]):
                    from flask import send_file
                    return send_file(self.current_challenge["image_path"])
                return "Image not found", 404
            
            @app.route('/submit_solution', methods=['POST'])
            def submit_solution():
                data = request.get_json()
                self.solution = data
                self.solution_ready.set()
                return jsonify({"success": True})
            
            @app.route('/skip', methods=['POST'])
            def skip():
                self.solution = None
                self.solution_ready.set()
                return jsonify({"success": True})
            
            # Start server in thread
            def run_server():
                app.run(host='localhost', port=self.port, debug=False, use_reloader=False)
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            time.sleep(1)  # Give server time to start
            
        except ImportError:
            raise RuntimeError("Flask is required for manual CAPTCHA solving. Install with: pip install flask")

class TwoCaptchaSolver:
    """Solves CAPTCHAs using 2Captcha service API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        
    def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """
        Solve CAPTCHA using 2Captcha service
        
        Args:
            challenge: The CAPTCHA challenge to solve
            
        Returns:
            CaptchaSolution with result
        """
        try:
            # Submit CAPTCHA to 2Captcha
            captcha_id = self._submit_captcha(challenge)
            if not captcha_id:
                return CaptchaSolution(
                    success=False,
                    error="Failed to submit CAPTCHA to 2Captcha",
                    method_used=CaptchaSolveMethod.TWOCAPTCHA
                )
            
            # Wait for solution
            solution = self._get_solution(captcha_id)
            if solution:
                return CaptchaSolution(
                    success=True,
                    solution=solution,
                    method_used=CaptchaSolveMethod.TWOCAPTCHA
                )
            else:
                return CaptchaSolution(
                    success=False,
                    error="Failed to get solution from 2Captcha",
                    method_used=CaptchaSolveMethod.TWOCAPTCHA
                )
                
        except Exception as e:
            return CaptchaSolution(
                success=False,
                error=f"2Captcha error: {str(e)}",
                method_used=CaptchaSolveMethod.TWOCAPTCHA
            )
    
    def _submit_captcha(self, challenge: CaptchaChallenge) -> Optional[str]:
        """Submit CAPTCHA image to 2Captcha service"""
        # Convert image to base64
        image_b64 = self._image_to_base64(challenge.image)
        
        # Submit to 2Captcha
        data = {
            'method': 'base64',
            'key': self.api_key,
            'body': image_b64
        }
        
        response = requests.post(f"{self.base_url}/in.php", data=data, timeout=30)
        result = response.text
        
        if result.startswith('OK|'):
            return result.split('|')[1]
        return None
    
    def _get_solution(self, captcha_id: str, max_wait: int = 120) -> Optional[str]:
        """Wait for and retrieve CAPTCHA solution"""
        url = f"{self.base_url}/res.php"
        
        for _ in range(max_wait // 5):
            params = {
                'key': self.api_key,
                'action': 'get',
                'id': captcha_id
            }
            
            response = requests.get(url, params=params, timeout=30)
            result = response.text
            
            if result == 'CAPCHA_NOT_READY':
                time.sleep(5)
                continue
            elif result.startswith('OK|'):
                return result.split('|')[1]
            else:
                return None
                
        return None
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert numpy image to base64 string"""
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
        pil_image = Image.fromarray(image_rgb)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

class CaptchaSolver:
    """Main CAPTCHA solving coordinator that manages all solving methods"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 twocaptcha_api_key: Optional[str] = None,
                 manual_port: int = 8899):
        
        self.detector = CaptchaDetector()
        self.openai_solver = OpenAICaptchaSolver(openai_api_key) if openai_api_key else None
        self.manual_solver = ManualCaptchaSolver(manual_port)
        self.twocaptcha_solver = TwoCaptchaSolver(twocaptcha_api_key) if twocaptcha_api_key else None
        
        # Default solving order
        self.solve_order = [CaptchaSolveMethod.OPENAI, CaptchaSolveMethod.MANUAL, CaptchaSolveMethod.TWOCAPTCHA]
    
    def detect_and_solve(self, screenshot: np.ndarray, 
                        methods: Optional[List[CaptchaSolveMethod]] = None) -> Optional[CaptchaSolution]:
        """
        Detect and solve CAPTCHA in screenshot
        
        Args:
            screenshot: Screenshot as numpy array
            methods: List of solving methods to try in order
            
        Returns:
            CaptchaSolution if solved, None if no CAPTCHA detected
        """
        
        # Detect CAPTCHA
        challenge = self.detector.detect_captcha(screenshot)
        if not challenge:
            return None
        
        print(f"🎯 CAPTCHA detected: {challenge.challenge_type} (confidence: {challenge.confidence:.2f})")
        
        # Try solving methods in order
        methods = methods or self.solve_order
        
        for method in methods:
            solver = self._get_solver(method)
            if not solver:
                continue
                
            print(f"🔄 Trying {method.value} method...")
            solution = solver.solve(challenge)
            
            if solution.success:
                print(f"✅ CAPTCHA solved using {method.value}")
                return solution
            else:
                print(f"❌ {method.value} failed: {solution.error}")
        
        print("❌ All CAPTCHA solving methods failed")
        return CaptchaSolution(
            success=False,
            error="All solving methods failed"
        )
    
    def _get_solver(self, method: CaptchaSolveMethod):
        """Get appropriate solver for method"""
        if method == CaptchaSolveMethod.OPENAI:
            return self.openai_solver
        elif method == CaptchaSolveMethod.MANUAL:
            return self.manual_solver
        elif method == CaptchaSolveMethod.TWOCAPTCHA:
            return self.twocaptcha_solver
        return None
