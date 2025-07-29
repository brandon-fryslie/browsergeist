# BrowserGeist Testing Guide

This document provides comprehensive information about testing in the BrowserGeist project, including how to run tests, test architecture overview, and planned testing coverage.

## Quick Start

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies
uv pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_captcha_detection.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest -m integration

# Run with coverage reporting
pytest --cov=src/python_sdk --cov-report=html
```

### Test Environment Setup

```bash
# Ensure daemon is running for integration tests
./bin/browsergeist-daemon &

# Set environment variables for API testing (optional)
export OPENAI_API_KEY="your-key-here"
export TWOCAPTCHA_API_KEY="your-key-here"
```

## Test Architecture Overview

### Testing Principles

Our testing follows these core principles:
- **Real Behavior Testing**: Tests verify actual functionality, not mocked behavior
- **Layered Testing**: Unit tests for components, integration tests for interactions
- **Non-Tautological**: Mocks don't make tests automatically pass
- **Future-Proof**: Tests enable refactoring rather than hindering it
- **Comprehensive Coverage**: All new functionality must include tests

### Test Categories

#### 1. Unit Tests
Test individual components in isolation with minimal dependencies.

**Location**: `tests/test_*.py`
**Purpose**: Verify component behavior, edge cases, error handling
**Characteristics**: Fast, isolated, deterministic

#### 2. Integration Tests
Test component interactions and end-to-end workflows.

**Location**: `tests/integration/test_*.py`
**Markers**: `@pytest.mark.integration`
**Purpose**: Verify system integration, real API interactions
**Characteristics**: Slower, may require external services

#### 3. Performance Tests
Benchmark critical paths and detect performance regressions.

**Location**: `tests/performance/test_*.py`
**Markers**: `@pytest.mark.performance`
**Purpose**: Ensure acceptable performance characteristics
**Characteristics**: Time-sensitive, resource-intensive

## Current Test Coverage

### ✅ CAPTCHA System Tests (`test_captcha_detection.py`)

**Coverage**: CAPTCHA detection and recognition functionality

**Test Classes**:
- `TestCaptchaDetector`: Core detection functionality
  - Text-based CAPTCHA detection using OCR
  - Grid pattern recognition for image selection CAPTCHAs
  - Template matching with real image data
  - False positive prevention on normal webpages
  - Bounding box validation and coordinate checking
  - Grayscale image compatibility

- `TestCaptchaDetectionRobustness`: Edge cases and error handling
  - Empty/invalid image handling
  - Large image performance testing
  - Noise resistance verification
  - Multiple detection method coordination

- `TestCaptchaDetectionIntegration`: Real-world scenarios
  - Browser screenshot simulation testing
  - Performance benchmarking and regression detection
  - Realistic CAPTCHA placement validation

**Key Features Tested**:
- Multi-modal detection (template, OCR, pattern)
- Real image processing without mocked CV operations
- Performance characteristics with different image sizes
- Coordinate system validation
- Edge case robustness

### Test Fixtures and Utilities

**Image Generation Fixtures**:
- `sample_text_captcha`: Realistic text-based CAPTCHA with distorted text
- `sample_grid_captcha`: Grid-based image selection CAPTCHA simulation
- `normal_webpage`: Standard webpage without CAPTCHA elements

**Performance Benchmarking**:
- Real-time performance measurement
- Regression detection thresholds
- Scalability validation across image sizes

## Test Data and Assets

### Generated Test Images
Tests use programmatically generated images to ensure:
- Consistent test conditions
- No external dependencies
- Realistic CAPTCHA characteristics
- Controlled variations for edge case testing

### Template Directory Structure
```
tests/
├── fixtures/
│   ├── captcha_templates/
│   │   ├── recaptcha_v2.png
│   │   ├── hcaptcha.png
│   │   └── custom_captcha.png
│   └── sample_screenshots/
└── data/
    ├── performance_baselines.json
    └── detection_accuracy_metrics.json
```

## TODO: Tests Still to Write

### 🔄 High Priority Test Coverage Needed

#### CAPTCHA Solver Integration Tests
- **File**: `tests/test_captcha_solvers.py`
- **Coverage**: OpenAI API, Manual webserver, 2Captcha service integration
- **Tests Needed**:
  - OpenAI API response parsing with real API responses
  - Manual webserver Flask interface testing
  - 2Captcha service communication and polling
  - Fallback mechanism validation between solvers
  - Error handling for API failures and network issues
  - Solution execution testing (typing text, clicking coordinates)

#### HumanMouse CAPTCHA Integration Tests  
- **File**: `tests/test_browsergeist_captcha.py`
- **Coverage**: CAPTCHA integration within main automation framework
- **Tests Needed**:
  - Automatic CAPTCHA detection during automation workflows
  - CAPTCHA-aware click/type methods functionality
  - Screenshot capture and processing integration
  - Configuration validation for API keys and settings
  - Auto-solve vs manual-solve mode switching

#### Motion Engine Tests
- **File**: `tests/test_human_motion.py`
- **Coverage**: Advanced physics engine and movement generation
- **Tests Needed**:
  - Fitts' Law timing calculation accuracy
  - Bézier curve path generation and smoothness
  - Tremor and jitter randomization validation
  - Motion profile parameter adherence
  - Hand-eye coordination delay implementation
  - Overshoot correction multi-step behavior

#### Virtual HID Driver Tests
- **File**: `tests/test_virtual_drivers.py`
- **Coverage**: Enhanced mouse and keyboard drivers
- **Tests Needed**:
  - VirtualMouse stealth feature validation
  - VirtualKeyboard timing variation testing
  - MouseDriver protocol compliance
  - KeyboardDriver protocol compliance
  - Randomization and timing distribution analysis
  - Character frequency-based typing speed verification

### 🔄 Medium Priority Test Coverage Needed

#### Vision System Tests
- **File**: `tests/test_vision_system.py`
- **Coverage**: Template matching and screen capture
- **Tests Needed**:
  - TemplateMatcher accuracy with real screenshots
  - VisionCache performance and hit rate testing
  - Multi-scale template matching validation
  - Screenshot capture system integration
  - Template library management and loading

#### IPC Communication Tests
- **File**: `tests/test_daemon_communication.py`
- **Coverage**: Unix socket communication between Python SDK and Swift daemon
- **Tests Needed**:
  - Socket connection reliability and error recovery
  - Command serialization and deserialization
  - Protocol version compatibility
  - Concurrent request handling
  - Connection pooling and management

#### System Integration Tests
- **File**: `tests/integration/test_end_to_end.py`
- **Coverage**: Complete automation workflows
- **Tests Needed**:
  - Full browser automation scenarios
  - Multi-component interaction validation
  - Performance under realistic workloads
  - Error recovery across component boundaries
  - Memory usage and resource management

### 🔄 Low Priority Test Coverage Needed

#### CLI Interface Tests
- **File**: `tests/test_cli.py`
- **Coverage**: Command-line interface and configuration
- **Tests Needed**:
  - Command parsing and validation
  - Configuration file loading
  - Error reporting and user feedback
  - Help system and documentation

#### Security and Validation Tests
- **File**: `tests/test_security.py`
- **Coverage**: Input validation and security measures
- **Tests Needed**:
  - API key validation and secure storage
  - Input sanitization for commands
  - Permission and entitlement validation
  - Network security for API communications

#### Performance Regression Tests
- **File**: `tests/performance/test_performance_regression.py`
- **Coverage**: System-wide performance characteristics
- **Tests Needed**:
  - Automation speed benchmarking
  - Memory usage profiling
  - CPU utilization monitoring
  - Network efficiency measurement

## Test Writing Guidelines

### Effective Test Design

1. **Test Real Behavior**
   ```python
   # Good: Tests actual image processing
   def test_captcha_detection_with_real_image():
       detector = CaptchaDetector()
       image = create_realistic_captcha_image()
       result = detector.detect_captcha(image)
       assert result.confidence > 0.7
   
   # Bad: Tautological mock
   def test_captcha_detection_mocked():
       detector = CaptchaDetector()
       detector.detect_captcha = Mock(return_value=True)
       assert detector.detect_captcha(image) == True  # Always passes
   ```

2. **Layer-Appropriate Testing**
   ```python
   # Unit test: Component in isolation
   def test_motion_profile_timing_calculation():
       profile = MotionProfile.natural
       duration = calculate_fitts_law_duration(distance=100, target_width=20, profile=profile)
       assert 0.1 < duration < 2.0  # Reasonable range
   
   # Integration test: Component interaction
   def test_motion_engine_with_virtual_mouse():
       mouse = VirtualMouse()
       motion = HumanMotion(mouse, MotionProfile.natural)
       motion.moveTo((100, 100), (200, 200))
       # Verify real movement occurred
   ```

3. **Future-Proof Test Design**
   ```python
   # Good: Tests interface, allows implementation changes
   def test_captcha_solver_handles_text_solution():
       solver = AnyCaptchaSolver()
       challenge = create_text_challenge()
       solution = solver.solve(challenge)
       assert solution.success
       assert solution.solution is not None
   
   # Bad: Tests implementation details
   def test_captcha_solver_calls_specific_api():
       solver = OpenAICaptchaSolver()
       with patch('requests.post') as mock_post:
           solver.solve(challenge)
           mock_post.assert_called_once()  # Brittle implementation test
   ```

### Test Naming Conventions

- **Unit Tests**: `test_<component>_<behavior>`
- **Integration Tests**: `test_<system>_<interaction>_integration`  
- **Performance Tests**: `test_<feature>_performance`
- **Edge Cases**: `test_<component>_<edge_case>_handling`

### Fixture Design Principles

- **Realistic Data**: Use real or realistic test data
- **Parameterized**: Support multiple test scenarios
- **Isolated**: Each test gets fresh fixtures
- **Documented**: Clear purpose and usage

### Assertion Best Practices

- **Specific**: Assert exact expected behavior
- **Meaningful**: Provide context in assertion messages
- **Comprehensive**: Test success and failure paths
- **Boundary**: Test edge cases and limits

## Running Specific Test Categories

```bash
# Run only CAPTCHA tests
pytest tests/test_captcha_detection.py -v

# Run integration tests
pytest -m integration

# Run performance tests
pytest -m performance --tb=short

# Run tests with coverage
pytest --cov=src/python_sdk --cov-report=term-missing

# Run tests and generate HTML coverage report
pytest --cov=src/python_sdk --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

### Test Automation

Tests run automatically on:
- Pull request submission
- Main branch commits  
- Release candidate builds
- Nightly performance runs

### Coverage Requirements

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 95% coverage for core automation
- **API Interfaces**: 100% coverage for public APIs
- **Performance**: No regression beyond 10% of baseline

### Test Environment Matrix

Tests run across:
- macOS 12.0+ (primary target)
- Python 3.8, 3.9, 3.10, 3.11
- With/without optional dependencies
- Different API key configurations

## Troubleshooting Tests

### Common Issues

1. **Daemon Not Running**
   ```bash
   # Start daemon before integration tests
   ./bin/browsergeist-daemon &
   pytest tests/integration/
   ```

2. **Missing Dependencies**
   ```bash
   # Install all test dependencies
   uv pip install -r requirements.txt pytest pytest-asyncio
   ```

3. **API Key Issues**
   ```bash
   # Set optional API keys for full test coverage
   export OPENAI_API_KEY="your-key"
   export TWOCAPTCHA_API_KEY="your-key"
   ```

4. **Permission Issues**
   ```bash
   # Ensure proper permissions for screen capture
   # Check System Preferences > Security & Privacy > Screen Recording
   ```

### Test Debugging

```bash
# Run with maximum verbosity
pytest -vvv --tb=long

# Run single test with debugging
pytest tests/test_captcha_detection.py::TestCaptchaDetector::test_detect_text_based_captcha -vvv

# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s
```

## Contributing Test Code

When adding new functionality:

1. **Write tests first** (TDD approach preferred)
2. **Follow naming conventions** for discoverability  
3. **Include edge cases** and error conditions
4. **Document complex test logic** with comments
5. **Update this TESTING.md** with new test descriptions
6. **Ensure tests pass** before submitting PR

### Test Review Checklist

- [ ] Tests cover all new functionality
- [ ] Tests follow non-tautological principles
- [ ] Integration tests verify real component interactions
- [ ] Performance tests include regression detection
- [ ] Edge cases and error conditions covered
- [ ] Test names clearly describe what is being tested
- [ ] Fixtures provide realistic test data
- [ ] TESTING.md updated with new test information
