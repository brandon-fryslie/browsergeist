import Foundation
import CoreGraphics
import AppKit

/**
 * Core Graphics Mouse Driver
 * 
 * Uses Core Graphics events to simulate mouse input
 * This provides a more compatible alternative to IOHIDUserDevice
 */
class CGMouse: MouseDriver {
    private let queue = DispatchQueue(label: "mouse.events", qos: .userInitiated)
    
    struct MouseReport {
        var deltaX: Int = 0
        var deltaY: Int = 0
    }
    
    func initialize() -> Bool {
        // Check accessibility permissions
        let trusted = AXIsProcessTrusted()
        if !trusted {
            print("Warning: Accessibility permissions not granted. Mouse events may not work.")
            print("Please enable in System Preferences > Security & Privacy > Privacy > Accessibility")
        }
        return true
    }
    
    func moveDelta(_ dx: Int, _ dy: Int) {
        queue.async {
            let currentLocation = NSEvent.mouseLocation
            let newLocation = CGPoint(
                x: currentLocation.x + CGFloat(dx),
                y: currentLocation.y + CGFloat(dy)
            )
            
            // Create mouse movement event
            guard let event = CGEvent(
                mouseEventSource: nil,
                mouseType: .mouseMoved,
                mouseCursorPosition: newLocation,
                mouseButton: .left
            ) else {
                return
            }
            
            event.post(tap: .cghidEventTap)
        }
    }
    
    func click(button: MouseButton = .left, duration: TimeInterval = 0.05) {
        queue.async {
            let currentLocation = NSEvent.mouseLocation
            let location = CGPoint(x: currentLocation.x, y: currentLocation.y)
            
            let (downType, upType, cgButton) = self.buttonToCGEvent(button)
            
            // Mouse down
            guard let downEvent = CGEvent(
                mouseEventSource: nil,
                mouseType: downType,
                mouseCursorPosition: location,
                mouseButton: cgButton
            ) else {
                return
            }
            
            downEvent.post(tap: .cghidEventTap)
            
            // Hold for duration
            Thread.sleep(forTimeInterval: duration)
            
            // Mouse up
            guard let upEvent = CGEvent(
                mouseEventSource: nil,
                mouseType: upType,
                mouseCursorPosition: location,
                mouseButton: cgButton
            ) else {
                return
            }
            
            upEvent.post(tap: .cghidEventTap)
        }
    }
    
    func moveToAbsolute(_ x: Int, _ y: Int) {
        queue.async {
            let location = CGPoint(x: CGFloat(x), y: CGFloat(y))
            
            guard let event = CGEvent(
                mouseEventSource: nil,
                mouseType: .mouseMoved,
                mouseCursorPosition: location,
                mouseButton: .left
            ) else {
                return
            }
            
            event.post(tap: .cghidEventTap)
        }
    }
    
    func scroll(dx: Int, dy: Int) {
        queue.async {
            guard let event = CGEvent(
                scrollWheelEvent2Source: nil,
                units: .pixel,
                wheelCount: 2,
                wheel1: Int32(dy),
                wheel2: Int32(dx),
                wheel3: 0
            ) else {
                return
            }
            
            event.post(tap: .cghidEventTap)
        }
    }
    
    private func buttonToCGEvent(_ button: MouseButton) -> (CGEventType, CGEventType, CGMouseButton) {
        switch button {
        case .left:
            return (.leftMouseDown, .leftMouseUp, .left)
        case .right:
            return (.rightMouseDown, .rightMouseUp, .right)
        case .middle:
            return (.otherMouseDown, .otherMouseUp, .center)
        }
    }
}

enum MouseButton: UInt8 {
    case left = 0x01
    case right = 0x02
    case middle = 0x04
}
