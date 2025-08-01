Project Title:
Develop an Undetectable, Human-Like Browser Automation Framework for macOS Using a Custom Virtual HID Mouse Driver

⸻

Objective:
Create a modern, stealthy, and scriptable browser automation tool for macOS that simulates human interaction by injecting mouse and keyboard events through a custom HID device driver, constrained to mimic real user input at the USB or input system level. The tool should be usable for test automation against browsers (Safari, Chrome, Firefox) in a way that is impossible to detect, even by sophisticated anti-automation measures.

⸻

High-Level Goals:
1.	Undetectability:
      •	No use of browser automation frameworks (e.g., Playwright, Puppeteer, Selenium)
      •	No reliance on accessibility APIs, AppleScript, or DevTools protocols
      •	Mouse and keyboard events must be indistinguishable from a real HID device
2.	Input Injection Method:
      •	Implement a virtual HID device (mouse and optionally keyboard) via a custom kernel extension (DriverKit or IOKit) or a user-space driver using HIDUserDevice
      •	Inject events using constrained movement profiles, click timing, and behavioral randomness to emulate humans
3.	Constraint System for Human Likeness:
      •	Enforce acceleration curves, dwell times, velocity jitter, and non-instantaneous movement
      •	Model hand-eye coordination (delay between target appearance and response)
      •	Typing to include key travel delays and fingerprint-safe timing variation
4.	Target Acquisition & Vision Layer:
      •	Use OpenCV for on-screen visual target detection (template matching or ML-based)
      •	Optional: Tesseract OCR for dynamic content targeting
      •	Output click targets in absolute screen coordinates
5.	Scripting Interface:
•	Modern Python 3.x API, clean and ergonomic:
6.	Robust Wait System:
	•	Comprehensive waiting mechanisms for UI stability and element readiness
	•	Playwright-inspired API for reliable automation timing
	•	Built-in assertions with automatic waiting and retries
	•	Prevention of dangerous actions when UI elements are not ready
6. CAPTCHA solving via 3 methods: OpenAI API, user notification w/ link to private internal webserver allowing user to solve it directly, 2Captcha api integration
6. Integration with OpenAI API that allows sending a screenshot (or relevant section of screenshot) to the API along with a prompt.  This screenshot and prompt are designed such that the API will return browsergeist commands that will complete any CAPTCHA in the image
7. If a CAPTCHA is detected and unable to be completed by OpenAI API, browsergeist sends a notification to the user that includes a link to a small web-server run by browsergeist.  A page on this web server shows the CAPTCHA.  The user can complete the captcha for browsergeist to move to the next part of the automation.  
8. browsergeist also integrates with the 2Captcha API for solving captchas
9. Example library - project contains an extensive example library containing working examples of each individual functionality, as well as examples of any non-trivial functionalities. All examples must contain fully functional, real implementations with no simulated or placeholder functionality.
10. Code Quality Standard: No simulated or placeholder functionality is acceptable in production code or examples. All code must be fully functional and demonstrate real working capabilities.

bot = HumanMouse()
bot.move_to(target("login_button.png"))
bot.click()
bot.type("user@example.com", delay_profile="average")


	•	Include CLI test runner and headless scripting mode

	6.	System Integration:
	•	macOS: implement proper entitlements and TCC permissions (input monitoring, screen recording, etc.)
	•	Respect SIP boundaries or provide workaround instructions for kexts if required

⸻

Technical Deliverables:
1.	✅ HID Mouse Driver (DriverKit or user-space with HIDUserDevice)
      •	Moves the system cursor and generates native clicks
      •	Accepts input events from user-space daemon
2.	✅ User-Space Control Daemon
      •	Listens to Python commands via IPC (e.g., UNIX socket, gRPC, or ZeroMQ)
      •	Enforces motion constraints and feeds events to HID device
3.	✅ Python SDK
      •	Exposes testable API for defining automation scripts
      •	Includes motion planning, randomization modules, and visual targeting
      •	API includes full async support, which is the primary and recommended usage
4.	✅ Vision Module
      •	OpenCV-based image locator
      •	Optional: OCR or ML classifier for dynamic elements
5.	✅ Permissions Setup
      •	Full documentation for TCC, System Extensions, and signing
      •	Hardened Runtime compliant if necessary
6. Include a 'recording' mode where I can manually perform some actions on the computer and browsergeist will save the actions as working browsergeist code, allowing me to reply the actions.  This includes screenshots to guide browsergeist so it can successfully perform the saved actions regardless of window position, size, etc
6. Thorough example library, containing a wide depth and breadth of examples and 'write-ups' of how to use the library for various complex scenarios such as completing a form on a web page.

⸻

Security/Stealth Goals:
•	The browser must not detect automation via:
•	navigator.webdriver
•	GPU/CPU timing patterns
•	Non-human click intervals
•	Cursor movement anomalies
•	Mimic all plausible biometrics of human input using constrained signal generation.

⸻

Milestones:
1.	Research macOS HID injection mechanisms (DriverKit vs HIDUserDevice)
2.	Prototype virtual mouse driver
3.	Build motion constraint engine
4.	Integrate OpenCV for visual acquisition
5.	Design Python interface and CLI
6.	Validate against live Chrome/Firefox sessions
7.	Write full documentation and reproducible install process

⸻

Final Deliverable:
A stealth-native, physically indistinguishable browser automation framework for macOS using a virtual HID mouse, constrained to realistic human behavior, scriptable via Python, and fully compatible with visual GUI targeting.
