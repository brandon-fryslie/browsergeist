import Foundation
import CoreGraphics
import AppKit

/**
 * Control Daemon
 *
 * Bridges between the Python SDK and the HID driver,
 * handling IPC communication and coordinating mouse actions.
 */
class ControlDaemon {
    private let socketPath = "/tmp/browsergeist.sock"
    private var server: UnixSocketServer?

    private let mouse: VirtualMouse
    private let keyboard: VirtualKeyboard
    private let motionEngine: HumanMotion

    init() {
        self.mouse = VirtualMouse()
        self.keyboard = VirtualKeyboard()
        self.motionEngine = HumanMotion(mouse: mouse)

        guard mouse.initialize() else {
            fatalError("Failed to initialize mouse")
        }

        guard keyboard.initialize() else {
            fatalError("Failed to initialize keyboard")
        }
    }

    func start() throws {
        server = UnixSocketServer(socketPath: socketPath)

        try server?.start { [weak self] clientSocket in
            self?.handleConnection(clientSocket)
        }

        print("Control daemon listening on \(socketPath)")

        // Keep the daemon running
        RunLoop.current.run()
    }

    private func handleConnection(_ clientSocket: Int32) {
        let connection = SocketConnection(socket: clientSocket)

        while true {
            guard let messageData = connection.readMessage() else {
                break
            }

            let response = processMessage(messageData)

            guard let responseData = try? JSONSerialization.data(withJSONObject: response) else {
                break
            }

            if !connection.sendMessage(responseData) {
                break
            }
        }
    }

    private func processMessage(_ data: Data) -> [String: Any] {
        guard let jsonString = String(data: data, encoding: .utf8),
              let jsonData = jsonString.data(using: .utf8),
              let command = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
              let action = command["action"] as? String else {
            return ["success": false, "error": "Invalid command"]
        }

        switch action {
        case "move_to":
            return handleMoveTo(command)
        case "click":
            return handleClick(command)
        case "type":
            return handleType(command)
        case "scroll":
            return handleScroll(command)
        case "screenshot":
            return handleScreenshot()
        case "key_combination":
            return handleKeyCombination(command)
        case "find_element_by_text":
            return handleFindElementByText(command)
        case "find_input_field":
            return handleFindInputField(command)
        case "find_button":
            return handleFindButton(command)
        default:
            return ["success": false, "error": "Unknown action: \(action)"]
        }
    }

    private func handleMoveTo(_ command: [String: Any]) -> [String: Any] {
        guard let x = command["x"] as? Double,
              let y = command["y"] as? Double else {
            return ["success": false, "error": "Missing x,y coordinates"]
        }

        let currentMouseLocation = NSEvent.mouseLocation
        let target = CGPoint(x: x, y: y)
        let current = CGPoint(x: currentMouseLocation.x, y: currentMouseLocation.y)

        // Apply motion profile if provided
        var profile = HumanMotion.MotionProfile.natural
        if let profileData = command["profile"] as? [String: Any] {
            profile = parseMotionProfile(profileData)
        }

        let motion = HumanMotion(mouse: mouse, profile: profile)
        motion.moveTo(target: target, from: current)

        return ["success": true]
    }

    private func handleClick(_ command: [String: Any]) -> [String: Any] {
        let buttonString = command["button"] as? String ?? "left"
        let duration = command["duration"] as? TimeInterval ?? 0.05

        let button: MouseButton
        switch buttonString {
        case "left": button = .left
        case "right": button = .right
        case "middle": button = .middle
        default: button = .left
        }

        mouse.click(button: button, duration: duration)
        return ["success": true]
    }

    private func handleType(_ command: [String: Any]) -> [String: Any] {
        guard let text = command["text"] as? String else {
            return ["success": false, "error": "Missing text"]
        }

        let delayProfileString = command["delay_profile"] as? String ?? "average"

        let typingProfile: TypingProfile
        switch delayProfileString {
        case "fast": typingProfile = .fast
        case "careful": typingProfile = .careful
        case "natural": typingProfile = .natural
        default: typingProfile = .average
        }

        keyboard.typeTextSync(text, profile: typingProfile)

        return ["success": true]
    }

    private func handleScroll(_ command: [String: Any]) -> [String: Any] {
        let dx = command["dx"] as? Int ?? 0
        let dy = command["dy"] as? Int ?? 0
        let smooth = command["smooth"] as? Bool ?? true

        if smooth {
            // Implement smooth scrolling with multiple small movements
            let steps = max(abs(dx), abs(dy)) / 5
            let stepDx = dx / max(steps, 1)
            let stepDy = dy / max(steps, 1)

            for _ in 0..<steps {
                mouse.scroll(dx: stepDx, dy: stepDy)
                Thread.sleep(forTimeInterval: 0.01)
            }
        } else {
            mouse.scroll(dx: dx, dy: dy)
        }

        return ["success": true]
    }

    private func handleScreenshot() -> [String: Any] {
        do {
            let image = try ScreenCapture.captureFullScreenSync()
            let imageData = try ScreenCapture.imageToData(image, format: "png")
            let base64String = imageData.base64EncodedString()

            return ["success": true, "data": base64String, "format": "png"]
        } catch {
            return ["success": false, "error": "Failed to capture screenshot: \(error.localizedDescription)"]
        }
    }
    
    private func handleKeyCombination(_ command: [String: Any]) -> [String: Any] {
        guard let keys = command["keys"] as? [String] else {
            return ["success": false, "error": "Missing keys array"]
        }
        
        // Convert string keys to CGKeyCode
        var keyCodes: [CGKeyCode] = []
        var modifierFlags: CGEventFlags = []
        
        for key in keys {
            switch key.lowercased() {
            case "cmd", "command":
                modifierFlags.insert(.maskCommand)
            case "option", "alt":
                modifierFlags.insert(.maskAlternate)
            case "shift":
                modifierFlags.insert(.maskShift)
            case "ctrl", "control":
                modifierFlags.insert(.maskControl)
            case "a":
                keyCodes.append(0x00) // A key
            case "c":
                keyCodes.append(0x08) // C key
            case "v":
                keyCodes.append(0x09) // V key
            case "x":
                keyCodes.append(0x07) // X key
            case "z":
                keyCodes.append(0x06) // Z key
            default:
                // Try to map other common keys
                if let keyCode = mapStringToKeyCode(key) {
                    keyCodes.append(keyCode)
                } else {
                    return ["success": false, "error": "Unknown key: \(key)"]
                }
            }
        }
        
        // Send key combination
        for keyCode in keyCodes {
            let keyDownEvent = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: true)
            keyDownEvent?.flags = modifierFlags
            keyDownEvent?.post(tap: .cghidEventTap)
            
            Thread.sleep(forTimeInterval: 0.01) // Small delay
            
            let keyUpEvent = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: false)
            keyUpEvent?.flags = modifierFlags
            keyUpEvent?.post(tap: .cghidEventTap)
        }
        
        return ["success": true]
    }
    
    private func mapStringToKeyCode(_ key: String) -> CGKeyCode? {
        // Map common keys to their CGKeyCode values
        let keyMap: [String: CGKeyCode] = [
            "return": 0x24,
            "enter": 0x24,
            "tab": 0x30,
            "space": 0x31,
            "delete": 0x33,
            "escape": 0x35,
            "left": 0x7B,
            "right": 0x7C,
            "down": 0x7D,
            "up": 0x7E
        ]
        
        return keyMap[key.lowercased()]
    }
    
    private func handleFindElementByText(_ command: [String: Any]) -> [String: Any] {
        guard let text = command["text"] as? String else {
            return ["success": false, "error": "Missing text parameter"]
        }
        
        let bundleId = command["bundle_id"] as? String
        
        if let coordinates = AccessibilityTargeting.findClickableElementByText(text, bundleId: bundleId) {
            return [
                "success": true,
                "x": coordinates.x,
                "y": coordinates.y,
                "method": "accessibility"
            ]
        } else {
            return ["success": false, "error": "Element not found: \(text)"]
        }
    }
    
    private func handleFindInputField(_ command: [String: Any]) -> [String: Any] {
        guard let labelText = command["label"] as? String else {
            return ["success": false, "error": "Missing label parameter"]
        }
        
        let bundleId = command["bundle_id"] as? String
        
        if let coordinates = AccessibilityTargeting.findInputFieldByLabel(labelText, bundleId: bundleId) {
            return [
                "success": true,
                "x": coordinates.x,
                "y": coordinates.y,
                "method": "accessibility"
            ]
        } else {
            return ["success": false, "error": "Input field not found: \(labelText)"]
        }
    }
    
    private func handleFindButton(_ command: [String: Any]) -> [String: Any] {
        guard let buttonText = command["text"] as? String else {
            return ["success": false, "error": "Missing text parameter"]
        }
        
        let bundleId = command["bundle_id"] as? String
        
        if let coordinates = AccessibilityTargeting.findButtonByText(buttonText, bundleId: bundleId) {
            return [
                "success": true,
                "x": coordinates.x,
                "y": coordinates.y,
                "method": "accessibility"
            ]
        } else {
            return ["success": false, "error": "Button not found: \(buttonText)"]
        }
    }

    private func parseMotionProfile(_ data: [String: Any]) -> HumanMotion.MotionProfile {
        return HumanMotion.MotionProfile(
            maxVelocity: data["max_velocity"] as? Double ?? 800.0,
            acceleration: data["acceleration"] as? Double ?? 2000.0,
            jitterAmount: data["jitter_amount"] as? Double ?? 2.0,
            overshootChance: data["overshoot_chance"] as? Double ?? 0.15,
            dwellTimeRange: (data["dwell_time_min"] as? TimeInterval ?? 0.02)...(data["dwell_time_max"] as? TimeInterval ?? 0.08),
            fittsLawA: data["fitts_law_a"] as? Double ?? 0.1,
            fittsLawB: data["fitts_law_b"] as? Double ?? 0.15,
            tremorIntensity: data["tremor_intensity"] as? Double ?? 0.5,
            handEyeDelay: (data["hand_eye_delay_min"] as? TimeInterval ?? 0.05)...(data["hand_eye_delay_max"] as? TimeInterval ?? 0.15),
            pathCurvature: data["path_curvature"] as? Double ?? 0.3
        )
    }

    private func getKeyDelay(for profile: String) -> TimeInterval {
        switch profile {
        case "fast": return TimeInterval.random(in: 0.05...0.1)
        case "careful": return TimeInterval.random(in: 0.15...0.3)
        case "average": return TimeInterval.random(in: 0.08...0.15)
        default: return TimeInterval.random(in: 0.08...0.15)
        }
    }


}
