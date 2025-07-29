import Foundation
import IOKit
import IOKit.hid

/**
 * Mouse Protocol
 * 
 * Common interface for both virtual and Core Graphics mouse implementations
 */
protocol MouseDriver {
    func initialize() -> Bool
    func moveDelta(_ dx: Int, _ dy: Int)
    func click(button: MouseButton, duration: TimeInterval)
    func moveToAbsolute(_ x: Int, _ y: Int)
    func scroll(dx: Int, dy: Int)
}

/**
 * Virtual HID Mouse Driver
 * 
 * Enhanced mouse driver with stealth features. Currently uses Core Graphics
 * with additional randomization and stealth enhancements.
 * TODO: Implement true IOHIDUserDevice when APIs are available.
 */
class VirtualMouse: MouseDriver {
    private let queue = DispatchQueue(label: "mouse.events", qos: .userInitiated)
    private let cgMouse = CGMouse() // Enhanced Core Graphics implementation
    
    func initialize() -> Bool {
        // Initialize the fallback Core Graphics mouse
        let success = cgMouse.initialize()
        
        // Add randomization seed for enhanced stealth
        srand48(Int(Date().timeIntervalSince1970))
        
        return success
    }
    
    func moveDelta(_ dx: Int, _ dy: Int) {
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Add micro-randomization for enhanced stealth
            let jitterX = Int(drand48() * 2.0 - 1.0) // Random jitter ±1 pixel
            let jitterY = Int(drand48() * 2.0 - 1.0)
            
            let adjustedDx = dx + jitterX
            let adjustedDy = dy + jitterY
            
            // Use Core Graphics as fallback with enhanced timing
            self.cgMouse.moveDelta(adjustedDx, adjustedDy)
            
            // Add micro-delay for more human-like timing
            let delay = drand48() * 0.001 // 0-1ms random delay
            Thread.sleep(forTimeInterval: delay)
        }
    }
    
    func click(button: MouseButton = .left, duration: TimeInterval = 0.05) {
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Add randomized click duration for enhanced stealth
            let baseVariation = drand48() * 0.02 - 0.01 // ±10ms variation
            let adjustedDuration = max(0.01, duration + baseVariation)
            
            // Use Core Graphics as fallback with enhanced timing
            self.cgMouse.click(button: button, duration: adjustedDuration)
            
            // Add post-click micro-delay
            let postDelay = drand48() * 0.005 // 0-5ms random delay
            Thread.sleep(forTimeInterval: postDelay)
        }
    }
    
    func moveToAbsolute(_ x: Int, _ y: Int) {
        // Delegate to Core Graphics implementation with stealth enhancements
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Add micro-jitter to absolute positioning
            let jitterX = Int(drand48() * 2.0 - 1.0)
            let jitterY = Int(drand48() * 2.0 - 1.0)
            
            self.cgMouse.moveToAbsolute(x + jitterX, y + jitterY)
            
            // Add micro-delay
            let delay = drand48() * 0.002 // 0-2ms random delay
            Thread.sleep(forTimeInterval: delay)
        }
    }
    
    func scroll(dx: Int, dy: Int) {
        // Enhanced scroll with randomization
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Add scroll randomization for more natural feel
            let scrollVariationX = Int(drand48() * 2.0 - 1.0)
            let scrollVariationY = Int(drand48() * 2.0 - 1.0)
            
            self.cgMouse.scroll(dx: dx + scrollVariationX, dy: dy + scrollVariationY)
            
            // Add scroll delay
            let delay = drand48() * 0.003 // 0-3ms random delay
            Thread.sleep(forTimeInterval: delay)
        }
    }
    
    deinit {
        // Cleanup handled by ARC
    }
}
