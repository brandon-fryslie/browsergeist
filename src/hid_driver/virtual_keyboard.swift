import Foundation
import CoreGraphics
import Carbon
import IOKit

/**
 * Virtual HID Keyboard Driver Protocol
 * 
 * Defines the interface for keyboard input injection implementations
 */
protocol KeyboardDriver {
    func initialize() -> Bool
    func pressKey(_ keyCode: CGKeyCode, modifiers: CGEventFlags, duration: TimeInterval) async
    func typeText(_ text: String, profile: TypingProfile) async
    func pressKeySequence(_ keys: [CGKeyCode], modifiers: CGEventFlags, delay: TimeInterval) async
}

/**
 * Enhanced Virtual Keyboard Driver
 * 
 * Provides keyboard input injection with advanced stealth features:
 * - Keystroke timing randomization
 * - Human-like typing patterns
 * - Per-character timing variations
 * - Typing rhythm modeling
 * - Anti-detection timing profiles
 */
final class VirtualKeyboard: KeyboardDriver, @unchecked Sendable {
    private let queue = DispatchQueue(label: "virtual.keyboard.events", qos: .userInitiated)
    private var isInitialized = false
    
    // Enhanced stealth configuration
    private struct StealthConfig {
        static let keyDurationVariation: ClosedRange<TimeInterval> = 0.03...0.08  // ±25ms key press duration
        static let interKeyVariation: ClosedRange<TimeInterval> = 0.005...0.015   // ±5-15ms between keys
        static let modifierHoldVariation: ClosedRange<TimeInterval> = 0.01...0.03 // ±10-30ms modifier timing
        static let fatigueFactor: Double = 1.0002 // Slight slowdown over time (0.02% per keystroke)
        static let burstTypingThreshold: Int = 5 // Keys typed rapidly before micro-pause
        static let microPauseChance: Double = 0.15 // 15% chance of micro-pause
        static let microPauseRange: ClosedRange<TimeInterval> = 0.05...0.15 // 50-150ms pause
    }
    
    // Character frequency for realistic timing (more common letters typed faster)
    private let characterFrequency: [Character: Double] = [
        "e": 12.7, "t": 9.1, "a": 8.2, "o": 7.5, "i": 7.0, "n": 6.7, "s": 6.3, "h": 6.1,
        "r": 6.0, "d": 4.3, "l": 4.0, "c": 2.8, "u": 2.8, "m": 2.4, "w": 2.4, "f": 2.2,
        "g": 2.0, "y": 2.0, "p": 1.9, "b": 1.3, "v": 1.0, "k": 0.8, "j": 0.15, "x": 0.15,
        "q": 0.1, "z": 0.07
    ]
    
    private var keystrokeCount: Int = 0
    private var lastKeystrokeTime: DispatchTime = .now()
    
    func initialize() -> Bool {
        // Check accessibility permissions
        let trusted = AXIsProcessTrusted()
        if !trusted {
            print("Warning: Accessibility permissions not granted. Keyboard events may not work.")
            print("Please enable in System Preferences > Security & Privacy > Privacy > Accessibility")
        }
        
        isInitialized = true
        keystrokeCount = 0
        return true
    }
    
    func pressKey(_ keyCode: CGKeyCode, modifiers: CGEventFlags = [], duration: TimeInterval = 0.05) async {
        await withUnsafeContinuation { continuation in
            queue.async {
                self.performKeyPress(keyCode, modifiers: modifiers, duration: duration)
                continuation.resume()
            }
        }
    }
    
    func typeText(_ text: String, profile: TypingProfile = .natural) async {
        await withUnsafeContinuation { continuation in
            queue.async {
                self.performTypeText(text, profile: profile)
                continuation.resume()
            }
        }
    }
    
    func pressKeySequence(_ keys: [CGKeyCode], modifiers: CGEventFlags = [], delay: TimeInterval = 0.1) async {
        await withUnsafeContinuation { continuation in
            queue.async {
                self.performKeySequence(keys, modifiers: modifiers, delay: delay)
                continuation.resume()
            }
        }
    }
    
    // MARK: - Synchronous Wrappers for Daemon Compatibility
    
    func typeTextSync(_ text: String, profile: TypingProfile = .natural) {
        // Direct synchronous implementation for daemon compatibility
        performTypeText(text, profile: profile)
    }
    
    func pressKeySync(_ keyCode: CGKeyCode, modifiers: CGEventFlags = [], duration: TimeInterval = 0.05) {
        // Direct synchronous implementation for daemon compatibility
        performKeyPress(keyCode, modifiers: modifiers, duration: duration)
    }
    
    // MARK: - Private Implementation with Stealth Features
    
    private func performKeyPress(_ keyCode: CGKeyCode, modifiers: CGEventFlags, duration: TimeInterval) {
        // Add stealth timing variations
        let enhancedDuration = duration + TimeInterval.random(in: StealthConfig.keyDurationVariation)
        let preDelay = TimeInterval.random(in: StealthConfig.interKeyVariation)
        
        // Micro-delay before keypress
        Thread.sleep(forTimeInterval: preDelay)
        
        // Key down event with enhanced timing
        guard let keyDownEvent = CGEvent(
            keyboardEventSource: nil,
            virtualKey: keyCode,
            keyDown: true
        ) else {
            return
        }
        
        keyDownEvent.flags = modifiers
        keyDownEvent.post(tap: .cghidEventTap)
        
        // Variable key hold duration with micro-randomization
        Thread.sleep(forTimeInterval: enhancedDuration)
        
        // Key up event
        guard let keyUpEvent = CGEvent(
            keyboardEventSource: nil,
            virtualKey: keyCode,
            keyDown: false
        ) else {
            return
        }
        
        keyUpEvent.flags = modifiers
        keyUpEvent.post(tap: .cghidEventTap)
        
        // Track keystroke for fatigue modeling
        keystrokeCount += 1
        lastKeystrokeTime = .now()
    }
    
    private func performTypeText(_ text: String, profile: TypingProfile) {
        var burstCount = 0
        
        for (_, char) in text.enumerated() {
            if let keyInfo = characterToKeyCode(char) {
                // Calculate base delay from profile and character frequency
                let baseDelay = profile.baseDelay()
                let frequencyMultiplier = getCharacterTimingMultiplier(char)
                let fatigueMultiplier = calculateFatigueMultiplier()
                
                var totalDelay = baseDelay * frequencyMultiplier * fatigueMultiplier
                
                // Add micro-pause for burst typing prevention
                burstCount += 1
                if burstCount >= StealthConfig.burstTypingThreshold {
                    if Double.random(in: 0...1) < StealthConfig.microPauseChance {
                        totalDelay += TimeInterval.random(in: StealthConfig.microPauseRange)
                        burstCount = 0
                    }
                }
                
                // Add random variation to prevent mechanical timing
                totalDelay += TimeInterval.random(in: -totalDelay * 0.2...totalDelay * 0.2)
                
                Thread.sleep(forTimeInterval: totalDelay)
                
                // Enhanced key press with stealth timing
                let keyDuration = profile.keyDuration() + TimeInterval.random(in: StealthConfig.keyDurationVariation)
                performKeyPress(keyInfo.keyCode, modifiers: keyInfo.modifiers, duration: keyDuration)
                
                // Variable inter-key timing
                let interKeyDelay = TimeInterval.random(in: StealthConfig.interKeyVariation)
                Thread.sleep(forTimeInterval: interKeyDelay)
            }
        }
    }
    
    private func performKeySequence(_ keys: [CGKeyCode], modifiers: CGEventFlags, delay: TimeInterval) {
        for (index, keyCode) in keys.enumerated() {
            // Enhanced timing for key sequences
            let enhancedDelay = delay + TimeInterval.random(in: StealthConfig.interKeyVariation)
            performKeyPress(keyCode, modifiers: modifiers, duration: 0.05)
            
            if index < keys.count - 1 {
                Thread.sleep(forTimeInterval: enhancedDelay)
            }
        }
    }
    
    private func getCharacterTimingMultiplier(_ char: Character) -> Double {
        let frequency = characterFrequency[Character(char.lowercased())] ?? 1.0
        // More frequent characters are typed faster (inverse relationship)
        return max(0.7, 2.0 - (frequency / 10.0))
    }
    
    private func calculateFatigueMultiplier() -> Double {
        // Subtle typing slowdown over time (realistic fatigue modeling)
        return pow(StealthConfig.fatigueFactor, Double(keystrokeCount))
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

// MARK: - Enhanced Typing Profile System

extension TypingProfile {
    func baseDelay() -> TimeInterval {
        switch self {
        case .fast:
            return TimeInterval.random(in: 0.04...0.08)
        case .average:
            return TimeInterval.random(in: 0.08...0.15)
        case .careful:
            return TimeInterval.random(in: 0.15...0.25)
        case .natural:
            // Natural typing with realistic pauses and variations
            let baseDelay = TimeInterval.random(in: 0.06...0.14)
            // 8% chance of longer thinking pause
            if Double.random(in: 0...1) < 0.08 {
                return baseDelay + TimeInterval.random(in: 0.2...0.6)
            }
            // 3% chance of backspace correction (very short pause)
            if Double.random(in: 0...1) < 0.03 {
                return baseDelay * 0.3
            }
            return baseDelay
        }
    }
    
    func keyDuration() -> TimeInterval {
        switch self {
        case .fast:
            return TimeInterval.random(in: 0.03...0.05)
        case .average:
            return TimeInterval.random(in: 0.04...0.07)
        case .careful:
            return TimeInterval.random(in: 0.06...0.1)
        case .natural:
            return TimeInterval.random(in: 0.035...0.085)
        }
    }
}
