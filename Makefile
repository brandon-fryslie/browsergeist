# BrowserGeist Build System

.PHONY: all build clean install daemon python test

# Default target
all: build

# Build the Swift daemon
build:
	@echo "Building control daemon..."
	swiftc -o bin/browsergeist-daemon \
		src/daemon/main.swift \
		src/daemon/control_daemon.swift \
		src/daemon/unix_server.swift \
		src/hid_driver/virtual_mouse.swift \
		src/hid_driver/cg_mouse.swift \
		src/hid_driver/virtual_keyboard.swift \
		src/hid_driver/cg_keyboard.swift \
		src/motion_engine/human_motion.swift \
		src/vision/screen_capture.swift \
		src/accessibility/macos_accessibility.swift \
		-framework Foundation \
		-framework CoreGraphics \
		-framework AppKit \
		-framework ImageIO \
		-framework Carbon \
		-framework IOKit \
		-framework ScreenCaptureKit \
		-framework UniformTypeIdentifiers \
		-framework ApplicationServices \
		-O

# Install Python dependencies (requires uv package manager)
python:
	@echo "Installing Python dependencies with uv..."
	uv pip install -r requirements.txt

# Create necessary directories
dirs:
	mkdir -p bin logs

# Install (requires sudo for system permissions)
install: build dirs
	@echo "Installing BrowserGeist..."
	sudo cp bin/browsergeist-daemon /usr/local/bin/
	sudo chmod +x /usr/local/bin/browsergeist-daemon
	@echo "Installation complete."
	@echo "IMPORTANT: Grant the following permissions in System Preferences:"
	@echo "1. Privacy & Security > Input Monitoring"
	@echo "2. Privacy & Security > Screen Recording"
	@echo "3. Privacy & Security > Accessibility (if needed)"

# Start the daemon
daemon: build dirs
	@echo "Starting BrowserGeist daemon..."
	./bin/browsergeist-daemon

# Run tests
test: build python
	@echo "Running tests..."
	python3 -m pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf bin/
	rm -f /tmp/browsergeist.sock

# Setup development environment
dev-setup: python dirs
	@echo "Setting up development environment..."
	@echo "Please ensure you have:"
	@echo "1. Xcode Command Line Tools installed"
	@echo "2. Input Monitoring permissions granted"
	@echo "3. Screen Recording permissions granted"
	@echo "4. Run 'uv pip install -r requirements.txt' for Python dependencies"

# Sign the binary with entitlements
sign: build
	@echo "Signing daemon with entitlements..."
	codesign --force --options runtime --entitlements entitlements.plist -s - bin/browsergeist-daemon

# Quick test of the Python SDK
demo: build daemon
	python3 examples/simple_demo.py
