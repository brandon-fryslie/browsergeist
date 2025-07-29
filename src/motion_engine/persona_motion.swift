import Foundation
import CoreGraphics
import QuartzCore
import Darwin

/**
 * Persona-Aware Motion Engine
 * 
 * Extends the human motion engine to support realistic user personas with
 * distinct behavioral patterns. Each persona has unique characteristics for:
 * - Movement speed and precision
 * - Timing patterns and hesitation
 * - Error correction behavior
 * - Fatigue and session state
 */
class PersonaMotion {
    
    struct PersonaMotionProfile {
        let baseSpeed: Double
        let speedVariance: Double
        let accelerationPreference: Double
        let precisionLevel: Double
        let overshootTendency: Double
        let correctionAttempts: ClosedRange<Int>
        let dwellTimeRange: ClosedRange<TimeInterval>
        let curvaturePreference: Double
        let microMovements: Bool
        let tremorIntensity: Double
        let hesitationTendency: Double
        let decisionSpeed: Double
        
        // Dynamic state factors
        var energyLevel: Double = 1.0
        var focusLevel: Double = 1.0
        var fatigueAccumulation: Double = 0.0
        
        // Persona-specific profiles
        static let techProfessional = PersonaMotionProfile(
            baseSpeed: 1200.0,
            speedVariance: 0.15,
            accelerationPreference: 1.8,
            precisionLevel: 0.9,
            overshootTendency: 0.05,
            correctionAttempts: 1...2,
            dwellTimeRange: 0.02...0.05,
            curvaturePreference: 0.2,
            microMovements: true,
            tremorIntensity: 0.3,
            hesitationTendency: 0.05,
            decisionSpeed: 1.8
        )
        
        static let casualUser = PersonaMotionProfile(
            baseSpeed: 800.0,
            speedVariance: 0.25,
            accelerationPreference: 1.2,
            precisionLevel: 0.75,
            overshootTendency: 0.15,
            correctionAttempts: 1...3,
            dwellTimeRange: 0.05...0.15,
            curvaturePreference: 0.4,
            microMovements: true,
            tremorIntensity: 0.5,
            hesitationTendency: 0.2,
            decisionSpeed: 1.0
        )
        
        static let seniorUser = PersonaMotionProfile(
            baseSpeed: 400.0,
            speedVariance: 0.3,
            accelerationPreference: 0.8,
            precisionLevel: 0.6,
            overshootTendency: 0.3,
            correctionAttempts: 2...5,
            dwellTimeRange: 0.15...0.4,
            curvaturePreference: 0.6,
            microMovements: true,
            tremorIntensity: 0.8,
            hesitationTendency: 0.4,
            decisionSpeed: 0.6
        )
        
        func getAdjustedSpeed() -> Double {
            let variance = Double.random(in: -speedVariance...speedVariance)
            let energyFactor = energyLevel
            let fatigueFactor = max(0.7, 1.0 - fatigueAccumulation * 0.1)
            
            return baseSpeed * (1 + variance) * energyFactor * fatigueFactor
        }
        
        func getAdjustedPrecision() -> Double {
            let focusFactor = focusLevel
            let fatigueFactor = max(0.8, 1.0 - fatigueAccumulation * 0.05)
            
            return min(1.0, precisionLevel * focusFactor * fatigueFactor)
        }
        
        mutating func updateSessionState() {
            // Energy varies slowly
            energyLevel += Double.random(in: -0.05...0.05)
            energyLevel = max(0.5, min(1.5, energyLevel))
            
            // Focus can change more rapidly
            focusLevel += Double.random(in: -0.1...0.1)
            focusLevel = max(0.5, min(1.5, focusLevel))
        }
        
        mutating func accumulateFatigue(sessionMinutes: Double) {
            let fatigueRate: Double
            switch baseSpeed {
            case 1000...: fatigueRate = 0.01  // Expert users fatigue slower
            case 600..<1000: fatigueRate = 0.015  // Intermediate users
            default: fatigueRate = 0.02  // Beginners fatigue faster
            }
            
            fatigueAccumulation = min(0.5, sessionMinutes * fatigueRate)
        }
    }
    
    private var profile: PersonaMotionProfile
    private let mouseDriver: MouseDriver
    private let sessionStartTime: Date
    
    init(persona: PersonaMotionProfile, mouseDriver: MouseDriver) {
        self.profile = persona
        self.mouseDriver = mouseDriver
        self.sessionStartTime = Date()
    }
    
    func moveTo(target: CGPoint, from current: CGPoint, targetWidth: Double = 20.0) {
        // Update session state
        updateSessionState()
        
        // Add persona-specific hesitation
        if shouldHesitate() {
            let hesitationDelay = calculateHesitationDelay()
            Thread.sleep(forTimeInterval: hesitationDelay)
        }
        
        // Generate movement path with persona characteristics
        let path = generatePersonaAwarePath(from: current, to: target, targetWidth: targetWidth)
        
        // Execute path with persona timing
        executePersonaPath(path)
    }
    
    private func updateSessionState() {
        let sessionMinutes = Date().timeIntervalSince(sessionStartTime) / 60.0
        profile.updateSessionState()
        profile.accumulateFatigue(sessionMinutes: sessionMinutes)
    }
    
    private func shouldHesitate() -> Bool {
        return Double.random(in: 0...1) < profile.hesitationTendency
    }
    
    private func calculateHesitationDelay() -> TimeInterval {
        let baseDelay = profile.dwellTimeRange.upperBound * 2.0
        let decisionFactor = 2.0 - profile.decisionSpeed
        return TimeInterval.random(in: 0.1...(baseDelay * decisionFactor))
    }
    
    private func generatePersonaAwarePath(from start: CGPoint, to end: CGPoint, targetWidth: Double) -> [PersonaPoint] {
        let distance = sqrt(pow(end.x - start.x, 2) + pow(end.y - start.y, 2))
        let duration = calculatePersonaFittsLaw(distance: distance, targetWidth: targetWidth)
        
        // Generate basic path with persona curvature
        let controlPoints = generatePersonaCurvedPath(start: start, end: end)
        
        // Calculate number of steps based on persona precision
        let adjustedPrecision = profile.getAdjustedPrecision()
        let stepCount = max(15, Int(distance / (10.0 / adjustedPrecision)))
        
        var points: [PersonaPoint] = []
        let timeStep = duration / Double(stepCount)
        
        for i in 0...stepCount {
            let t = Double(i) / Double(stepCount)
            let basePoint = calculateBezierPoint(t: t, start: start, 
                                               control1: controlPoints.0, 
                                               control2: controlPoints.1, 
                                               end: end)
            
            // Apply persona-specific noise and tremor
            let noisyPoint = applyPersonaNoise(to: basePoint, progress: t)
            
            let timestamp = Double(i) * timeStep
            points.append(PersonaPoint(x: noisyPoint.x, y: noisyPoint.y, timestamp: timestamp))
        }
        
        return points
    }
    
    private func calculatePersonaFittsLaw(distance: Double, targetWidth: Double) -> Double {
        // Persona-specific Fitts' Law coefficients
        let a: Double
        let b: Double
        
        switch profile.baseSpeed {
        case 1000...: // Tech professional
            a = 0.1; b = 0.15
        case 600..<1000: // Casual user
            a = 0.15; b = 0.2
        default: // Senior user
            a = 0.2; b = 0.25
        }
        
        let adjustedA = a / profile.decisionSpeed
        let adjustedB = b / profile.decisionSpeed
        
        let fittsTime = adjustedA + adjustedB * log2(distance / targetWidth + 1)
        
        // Add persona-specific variance
        let variance = Double.random(in: -0.15...0.15)
        return max(0.1, fittsTime * (1 + variance))
    }
    
    private func generatePersonaCurvedPath(start: CGPoint, end: CGPoint) -> (CGPoint, CGPoint) {
        let distance = sqrt(pow(end.x - start.x, 2) + pow(end.y - start.y, 2))
        let curvatureAmount = distance * profile.curvaturePreference * Double.random(in: 0.5...1.5)
        
        let angle = atan2(end.y - start.y, end.x - start.x)
        let perpAngle = angle + .pi / 2
        
        let offset1 = curvatureAmount * Double.random(in: -1...1)
        let offset2 = curvatureAmount * Double.random(in: -1...1)
        
        let control1 = CGPoint(
            x: start.x + (end.x - start.x) / 3 + cos(perpAngle) * offset1,
            y: start.y + (end.y - start.y) / 3 + sin(perpAngle) * offset1
        )
        
        let control2 = CGPoint(
            x: start.x + 2 * (end.x - start.x) / 3 + cos(perpAngle) * offset2,
            y: start.y + 2 * (end.y - start.y) / 3 + sin(perpAngle) * offset2
        )
        
        return (control1, control2)
    }
    
    private func calculateBezierPoint(t: Double, start: CGPoint, control1: CGPoint, control2: CGPoint, end: CGPoint) -> CGPoint {
        let u = 1 - t
        let tt = t * t
        let uu = u * u
        let uuu = uu * u
        let ttt = tt * t
        
        return CGPoint(
            x: uuu * start.x + 3 * uu * t * control1.x + 3 * u * tt * control2.x + ttt * end.x,
            y: uuu * start.y + 3 * uu * t * control1.y + 3 * u * tt * control2.y + ttt * end.y
        )
    }
    
    private func applyPersonaNoise(to point: CGPoint, progress: Double) -> CGPoint {
        var noisyPoint = point
        
        // Apply tremor based on persona
        let tremorX = sin(progress * 8 * .pi) * profile.tremorIntensity * Double.random(in: 0.5...1.5)
        let tremorY = cos(progress * 6 * .pi) * profile.tremorIntensity * Double.random(in: 0.5...1.5)
        
        noisyPoint.x += tremorX
        noisyPoint.y += tremorY
        
        // Apply micro-movements if persona uses them
        if profile.microMovements {
            let microX = Double.random(in: -1...1) * (2.0 - profile.precisionLevel)
            let microY = Double.random(in: -1...1) * (2.0 - profile.precisionLevel)
            
            noisyPoint.x += microX
            noisyPoint.y += microY
        }
        
        return noisyPoint
    }
    
    private func executePersonaPath(_ path: [PersonaPoint]) {
        for point in path {
            // Move to point with persona-specific timing
            mouseDriver.moveTo(x: Int(point.x), y: Int(point.y))
            
            // Persona-specific inter-movement delay
            let baseDelay = 0.001 // 1ms base
            let personaDelay = baseDelay * (2.0 - profile.decisionSpeed)
            let jitterDelay = Double.random(in: 0...personaDelay)
            
            Thread.sleep(forTimeInterval: jitterDelay)
        }
        
        // Handle overshoot based on persona tendency
        if shouldOvershoot() {
            handlePersonaOvershoot(path.last!)
        }
    }
    
    private func shouldOvershoot() -> Bool {
        return Double.random(in: 0...1) < profile.overshootTendency
    }
    
    private func handlePersonaOvershoot(_ targetPoint: PersonaPoint) {
        let overshootDistance = Double.random(in: 5...20) * (1.0 - profile.precisionLevel)
        let overshootAngle = Double.random(in: 0...(2 * .pi))
        
        let overshootX = targetPoint.x + cos(overshootAngle) * overshootDistance
        let overshootY = targetPoint.y + sin(overshootAngle) * overshootDistance
        
        // Move to overshoot position
        mouseDriver.moveTo(x: Int(overshootX), y: Int(overshootY))
        
        // Correction attempts based on persona
        let attempts = Int.random(in: profile.correctionAttempts)
        
        for attempt in 1...attempts {
            let correctionDelay = TimeInterval.random(in: profile.dwellTimeRange) * Double(attempt)
            Thread.sleep(forTimeInterval: correctionDelay)
            
            // Gradually correct back to target
            let correctionFactor = Double(attempt) / Double(attempts)
            let correctedX = overshootX + (targetPoint.x - overshootX) * correctionFactor
            let correctedY = overshootY + (targetPoint.y - overshootY) * correctionFactor
            
            mouseDriver.moveTo(x: Int(correctedX), y: Int(correctedY))
        }
    }
}

struct PersonaPoint {
    let x: Double
    let y: Double
    let timestamp: Double
}

// Extension to create personas from names
extension PersonaMotion.PersonaMotionProfile {
    static func fromPersonaName(_ name: String) -> PersonaMotion.PersonaMotionProfile? {
        switch name.lowercased() {
        case "tech_professional", "alex":
            return .techProfessional
        case "casual_user", "sarah":
            return .casualUser
        case "senior_user", "robert":
            return .seniorUser
        default:
            return nil
        }
    }
}
