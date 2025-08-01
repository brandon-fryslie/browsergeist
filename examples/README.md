# BrowserGeist Example Library

This directory contains a comprehensive example library demonstrating the full capabilities of the BrowserGeist automation framework.

## 🌟 Featured Example: Facebook Signup Automation

**[`facebook_signup_automation.py`](facebook_signup_automation.py)** - A comprehensive real-world automation example demonstrating:

### 🎯 Complete Workflow
1. **Launch Safari via Spotlight** (Cmd+Space automation)
2. **Open Private Window** (Menu navigation)
3. **Navigate to Facebook.com** (Address bar targeting)
4. **Start Account Creation** (Button detection)
5. **Fill Registration Form** (Intelligent field targeting with `admin@vast.wang`)

### 🚀 Advanced Features Showcased
- **Natural Element Targeting**: Find UI elements by text instead of coordinates
- **Multi-Method Detection**: Accessibility API + OCR fallback for maximum reliability
- **Human Behavior Simulation**: Realistic typing patterns and movement
- **Intelligent Fallbacks**: Multiple candidate approaches for robust automation
- **System Integration**: Spotlight, menu navigation, keyboard shortcuts

### 💡 Educational Focus
- **Stops before submission** for safety and compliance
- **User confirmation required** before running
- **Comprehensive logging** for learning automation patterns
- **Error handling examples** for production-ready code

```bash
# Run the featured example
./run_example.sh examples/facebook_signup_automation.py
```

## 📚 Example Categories

### 🟢 Basic Examples (Getting Started)
- [`basic_mouse_control.py`](basic_mouse_control.py) - Fundamental mouse movements and clicking
- [`basic_keyboard_input.py`](basic_keyboard_input.py) - Text typing with different profiles
- [`motion_profiles_demo.py`](motion_profiles_demo.py) - Natural, Careful, and Fast movement styles
- [`simple_demo.py`](simple_demo.py) - Quick overview of core features

### 🔵 Vision & Template Matching
- [`template_matching_guide.py`](template_matching_guide.py) - Finding UI elements with images
- [`multi_scale_detection.py`](multi_scale_detection.py) - Working with different screen resolutions
- [`ocr_text_detection.py`](ocr_text_detection.py) - Finding and interacting with text elements
- [`visual_debugging.py`](visual_debugging.py) - Debug vision system and save screenshots

### 🟠 Real-World Automation Scenarios
- [`facebook_signup_automation.py`](facebook_signup_automation.py) - **NEW!** Complete browser automation workflow
- [`web_form_automation.py`](web_form_automation.py) - Complete form filling workflow
- [`login_automation.py`](login_automation.py) - Secure login with credential handling
- [`shopping_cart_demo.py`](shopping_cart_demo.py) - E-commerce automation example
- [`social_media_posting.py`](social_media_posting.py) - Automated content posting
- [`email_automation.py`](email_automation.py) - Email composition and sending

### 🟣 Advanced Features
- [`captcha_solving_complete.py`](captcha_solving_complete.py) - All CAPTCHA solving methods
- [`persona_automation_example.py`](persona_automation_example.py) - User behavior simulation
- [`async_automation.py`](async_automation.py) - Modern async/await automation
- [`error_handling_patterns.py`](error_handling_patterns.py) - Robust error recovery
- [`session_management.py`](session_management.py) - Managing complex automation sessions

### 🔴 Complex Workflows
- [`multi_tab_browser_automation.py`](multi_tab_browser_automation.py) - Managing multiple browser tabs
- [`data_extraction_workflow.py`](data_extraction_workflow.py) - Web scraping with human-like behavior
- [`automated_testing_suite.py`](automated_testing_suite.py) - UI testing framework integration
- [`workflow_orchestration.py`](workflow_orchestration.py) - Chaining multiple automation tasks

### 🟡 Production & Deployment
- [`configuration_examples.py`](configuration_examples.py) - Production configuration patterns
- [`logging_and_monitoring.py`](logging_and_monitoring.py) - Comprehensive logging setup
- [`ci_cd_integration.py`](ci_cd_integration.py) - Using BrowserGeist in CI/CD pipelines
- [`scaling_automation.py`](scaling_automation.py) - Large-scale automation strategies

### 🟤 Stealth & Anti-Detection
- [`stealth_validation.py`](stealth_validation.py) - Testing undetectability features
- [`browser_fingerprinting.py`](browser_fingerprinting.py) - Avoiding detection techniques
- [`timing_randomization.py`](timing_randomization.py) - Human-like timing patterns
- [`behavioral_mimicry.py`](behavioral_mimicry.py) - Advanced human behavior simulation

## 🚀 Quick Start

1. **Choose Your Starting Point:**
   - New to automation? Start with [`simple_demo.py`](simple_demo.py)
   - Want to automate forms? See [`web_form_automation.py`](web_form_automation.py)
   - Need CAPTCHA handling? Check [`captcha_solving_complete.py`](captcha_solving_complete.py)
   - Building production systems? Start with [`async_automation.py`](async_automation.py)

2. **Run an Example:**
   ```bash
   # Make sure daemon is running
   ./bin/browsergeist daemon start
   
   # Run an example
   cd examples
   python3 simple_demo.py
   ```

3. **Customize for Your Use Case:**
   - Copy an example that's close to your needs
   - Modify the coordinates and image targets
   - Add your specific automation logic

## 📋 Example Requirements

### Prerequisites
- macOS 12.0+ with BrowserGeist installed
- BrowserGeist daemon running (`./bin/browsergeist daemon start`)
- Required Python packages (automatically handled by virtual environment)

### Template Images
Some examples use template images for visual targeting. Create an `assets/` directory and add screenshots of UI elements you want to target:

```
examples/
├── assets/
│   ├── login_button.png
│   ├── submit_button.png
│   ├── email_field.png
│   └── password_field.png
└── ...example files...
```

### API Keys (Optional)
For CAPTCHA solving examples, set environment variables:
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export TWOCAPTCHA_API_KEY="your-2captcha-key"
```

## 🎯 Learning Path

### Beginner (New to Automation)
1. [`simple_demo.py`](simple_demo.py) - Overview of capabilities
2. [`basic_mouse_control.py`](basic_mouse_control.py) - Mouse movement basics
3. [`basic_keyboard_input.py`](basic_keyboard_input.py) - Text input basics
4. [`template_matching_guide.py`](template_matching_guide.py) - Finding UI elements

### Intermediate (Building Real Automation)
1. [`web_form_automation.py`](web_form_automation.py) - Form filling workflow
2. [`login_automation.py`](login_automation.py) - Login automation
3. [`error_handling_patterns.py`](error_handling_patterns.py) - Robust error handling
4. [`captcha_solving_complete.py`](captcha_solving_complete.py) - CAPTCHA handling

### Advanced (Production Deployment)
1. [`async_automation.py`](async_automation.py) - Modern async patterns
2. [`session_management.py`](session_management.py) - Complex session handling
3. [`workflow_orchestration.py`](workflow_orchestration.py) - Multi-task workflows
4. [`scaling_automation.py`](scaling_automation.py) - Large-scale deployment

## 💡 Best Practices

### 1. Human-Like Behavior
- Use appropriate motion profiles for your scenario
- Add realistic delays between actions
- Vary your automation patterns to avoid detection

### 2. Error Handling
- Always use try/catch blocks for automation steps
- Implement retry logic with exponential backoff
- Have fallback strategies for critical workflows

### 3. Template Management
- Keep template images up-to-date with UI changes
- Use multiple confidence levels for matching
- Consider multi-scale matching for different screen sizes

### 4. Performance
- Use async/await for high-throughput automation
- Implement connection pooling for multiple sessions
- Cache frequently used templates and configurations

## 🔧 Troubleshooting

### Common Issues

**"Daemon not running"**
```bash
./bin/browsergeist daemon start
./bin/browsergeist doctor  # Check system health
```

**"Template not found"**
- Verify template image exists and is current
- Try adjusting confidence threshold
- Use the visual debugging tools

**"Permission denied"**
- Grant Input Monitoring permissions in System Preferences
- Grant Screen Recording permissions if using vision features
- Check that daemon has proper entitlements

**"Import errors"**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
# Install missing dependencies
uv pip install -r requirements.txt
```

### Getting Help

1. **Check the logs:** `~/.browsergeist/logs/`
2. **Run diagnostics:** `./bin/browsergeist doctor`
3. **Debug interactively:** `./bin/browsergeist debug`
4. **Check daemon status:** `./bin/browsergeist daemon status`

## 📖 Documentation References

- [Main README](../README.md) - Project overview and setup
- [CLI Guide](../docs/cli_guide.md) - Command line interface usage
- [API Reference](../docs/api_reference.md) - Complete API documentation
- [Deployment Guide](../docs/deployment.md) - Production deployment guide

---

**Happy Automating!** 🤖

For questions, issues, or contributions, please see the main project documentation.
