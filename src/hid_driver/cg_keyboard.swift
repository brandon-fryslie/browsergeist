import Foundation
import CoreGraphics
import Carbon

/**
 * Core Graphics Keyboard Driver
 * 
 * Uses Core Graphics events to simulate keyboard input
 */
final class CGKeyboard: KeyboardDriver, @unchecked Sendable {
    private let queue = DispatchQueue(label: "keyboard.events", qos: .userInitiated)
    
    func initialize() -> Bool {
        // Check accessibility permissions
        let trusted = AXIsProcessTrusted()
        if !trusted {
            print("Warning: Accessibility permissions not granted. Keyboard events may not work.")
            print("Please enable in System Preferences > Security & Privacy > Privacy > Accessibility")
        }
        return true
    }
    
    func pressKey(_ keyCode: CGKeyCode, modifiers: CGEventFlags = [], duration: TimeInterval = 0.05) async {
        await withUnsafeContinuation { continuation in
            queue.async {
            // Key down
            guard let keyDownEvent = CGEvent(
                keyboardEventSource: nil,
                virtualKey: keyCode,
                keyDown: true
            ) else {
                return
            }
            
            keyDownEvent.flags = modifiers
            keyDownEvent.post(tap: .cghidEventTap)
            
            // Hold for duration
            Thread.sleep(forTimeInterval: duration)
            
            // Key up
            guard let keyUpEvent = CGEvent(
                keyboardEventSource: nil,
                virtualKey: keyCode,
                keyDown: false
            ) else {
                return
            }
            
            keyUpEvent.flags = modifiers
            keyUpEvent.post(tap: .cghidEventTap)
            
            continuation.resume()
            }
        }
    }
    
    func typeText(_ text: String, profile: TypingProfile = .average) async {
        await withUnsafeContinuation { continuation in
            queue.async {
            for char in text {
                if let keyInfo = self.characterToKeyCode(char) {
                    let delay = profile.randomDelay()
                    Thread.sleep(forTimeInterval: delay)
                    
                    // Synchronous key press for CGKeyboard
                    self.performKeyPress(keyInfo.keyCode, modifiers: keyInfo.modifiers, duration: 0.05)
                    
                    // Add slight variation in release timing
                    Thread.sleep(forTimeInterval: TimeInterval.random(in: 0.01...0.03))
                }
            }
            
            continuation.resume()
            }
        }
    }
    
    func pressKeySequence(_ keys: [CGKeyCode], modifiers: CGEventFlags = [], delay: TimeInterval = 0.1) async {
        await withUnsafeContinuation { continuation in
            queue.async {
                for keyCode in keys {
                    self.performKeyPress(keyCode, modifiers: modifiers, duration: 0.05)
                    if keyCode != keys.last {
                        Thread.sleep(forTimeInterval: delay)
                    }
                }
                
                continuation.resume()
            }
        }
    }
    
    // MARK: - Private Helper Methods
    
    private func performKeyPress(_ keyCode: CGKeyCode, modifiers: CGEventFlags, duration: TimeInterval) {
        // Key down
        guard let keyDownEvent = CGEvent(
            keyboardEventSource: nil,
            virtualKey: keyCode,
            keyDown: true
        ) else {
            return
        }
        
        keyDownEvent.flags = modifiers
        keyDownEvent.post(tap: .cghidEventTap)
        
        // Hold for duration
        Thread.sleep(forTimeInterval: duration)
        
        // Key up
        guard let keyUpEvent = CGEvent(
            keyboardEventSource: nil,
            virtualKey: keyCode,
            keyDown: false
        ) else {
            return
        }
        
        keyUpEvent.flags = modifiers
        keyUpEvent.post(tap: .cghidEventTap)
    }
    
    private func characterToKeyCode(_ char: Character) -> KeyInfo? {
        switch char {
        // Lowercase letters
        case "a": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_A), modifiers: [])
        case "b": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_B), modifiers: [])
        case "c": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_C), modifiers: [])
        case "d": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_D), modifiers: [])
        case "e": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_E), modifiers: [])
        case "f": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_F), modifiers: [])
        case "g": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_G), modifiers: [])
        case "h": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_H), modifiers: [])
        case "i": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_I), modifiers: [])
        case "j": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_J), modifiers: [])
        case "k": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_K), modifiers: [])
        case "l": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_L), modifiers: [])
        case "m": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_M), modifiers: [])
        case "n": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_N), modifiers: [])
        case "o": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_O), modifiers: [])
        case "p": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_P), modifiers: [])
        case "q": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Q), modifiers: [])
        case "r": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_R), modifiers: [])
        case "s": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_S), modifiers: [])
        case "t": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_T), modifiers: [])
        case "u": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_U), modifiers: [])
        case "v": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_V), modifiers: [])
        case "w": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_W), modifiers: [])
        case "x": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_X), modifiers: [])
        case "y": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Y), modifiers: [])
        case "z": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Z), modifiers: [])
        
        // Uppercase letters (with shift)
        case "A": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_A), modifiers: [.maskShift])
        case "B": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_B), modifiers: [.maskShift])
        case "C": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_C), modifiers: [.maskShift])
        case "D": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_D), modifiers: [.maskShift])
        case "E": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_E), modifiers: [.maskShift])
        case "F": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_F), modifiers: [.maskShift])
        case "G": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_G), modifiers: [.maskShift])
        case "H": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_H), modifiers: [.maskShift])
        case "I": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_I), modifiers: [.maskShift])
        case "J": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_J), modifiers: [.maskShift])
        case "K": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_K), modifiers: [.maskShift])
        case "L": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_L), modifiers: [.maskShift])
        case "M": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_M), modifiers: [.maskShift])
        case "N": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_N), modifiers: [.maskShift])
        case "O": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_O), modifiers: [.maskShift])
        case "P": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_P), modifiers: [.maskShift])
        case "Q": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Q), modifiers: [.maskShift])
        case "R": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_R), modifiers: [.maskShift])
        case "S": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_S), modifiers: [.maskShift])
        case "T": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_T), modifiers: [.maskShift])
        case "U": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_U), modifiers: [.maskShift])
        case "V": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_V), modifiers: [.maskShift])
        case "W": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_W), modifiers: [.maskShift])
        case "X": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_X), modifiers: [.maskShift])
        case "Y": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Y), modifiers: [.maskShift])
        case "Z": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Z), modifiers: [.maskShift])
        
        // Numbers
        case "1": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_1), modifiers: [])
        case "2": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_2), modifiers: [])
        case "3": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_3), modifiers: [])
        case "4": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_4), modifiers: [])
        case "5": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_5), modifiers: [])
        case "6": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_6), modifiers: [])
        case "7": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_7), modifiers: [])
        case "8": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_8), modifiers: [])
        case "9": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_9), modifiers: [])
        case "0": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_0), modifiers: [])
        
        // Special characters
        case " ": return KeyInfo(keyCode: CGKeyCode(kVK_Space), modifiers: [])
        case "\n": return KeyInfo(keyCode: CGKeyCode(kVK_Return), modifiers: [])
        case "\t": return KeyInfo(keyCode: CGKeyCode(kVK_Tab), modifiers: [])
        case "-": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Minus), modifiers: [])
        case "=": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Equal), modifiers: [])
        case "[": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_LeftBracket), modifiers: [])
        case "]": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_RightBracket), modifiers: [])
        case "\\": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Backslash), modifiers: [])
        case ";": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Semicolon), modifiers: [])
        case "'": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Quote), modifiers: [])
        case "`": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Grave), modifiers: [])
        case ",": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Comma), modifiers: [])
        case ".": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Period), modifiers: [])
        case "/": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Slash), modifiers: [])
        
        // Shifted special characters
        case "!": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_1), modifiers: [.maskShift])
        case "@": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_2), modifiers: [.maskShift])
        case "#": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_3), modifiers: [.maskShift])
        case "$": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_4), modifiers: [.maskShift])
        case "%": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_5), modifiers: [.maskShift])
        case "^": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_6), modifiers: [.maskShift])
        case "&": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_7), modifiers: [.maskShift])
        case "*": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_8), modifiers: [.maskShift])
        case "(": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_9), modifiers: [.maskShift])
        case ")": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_0), modifiers: [.maskShift])
        case "_": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Minus), modifiers: [.maskShift])
        case "+": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Equal), modifiers: [.maskShift])
        case "{": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_LeftBracket), modifiers: [.maskShift])
        case "}": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_RightBracket), modifiers: [.maskShift])
        case "|": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Backslash), modifiers: [.maskShift])
        case ":": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Semicolon), modifiers: [.maskShift])
        case "\"": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Quote), modifiers: [.maskShift])
        case "~": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Grave), modifiers: [.maskShift])
        case "<": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Comma), modifiers: [.maskShift])
        case ">": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Period), modifiers: [.maskShift])
        case "?": return KeyInfo(keyCode: CGKeyCode(kVK_ANSI_Slash), modifiers: [.maskShift])
        
        default:
            return nil
        }
    }
}

struct KeyInfo {
    let keyCode: CGKeyCode
    let modifiers: CGEventFlags
}

enum TypingProfile {
    case fast
    case average
    case careful
    case natural
    
    func randomDelay() -> TimeInterval {
        switch self {
        case .fast:
            return TimeInterval.random(in: 0.05...0.1)
        case .average:
            return TimeInterval.random(in: 0.08...0.15)
        case .careful:
            return TimeInterval.random(in: 0.15...0.3)
        case .natural:
            // More sophisticated timing with occasional longer pauses
            let baseDelay = TimeInterval.random(in: 0.08...0.12)
            // 5% chance of longer pause (thinking time)
            if Double.random(in: 0...1) < 0.05 {
                return baseDelay + TimeInterval.random(in: 0.3...0.8)
            }
            return baseDelay
        }
    }
}
