import Foundation
import CoreGraphics
import QuartzCore
import Darwin

/**
 * Advanced Human Motion Engine
 * 
 * Generates statistically indistinguishable human mouse movement patterns using:
 * - Fitts' Law timing calculations for realistic movement duration
 * - Bézier curve path generation with natural arc variation
 * - Micro-movements and tremor modeling
 * - Hand-eye coordination delays
 * - Multi-step overshoot correction
 */
class HumanMotion {
    
    struct MotionProfile {
        let maxVelocity: Double
        let acceleration: Double
        let jitterAmount: Double
        let overshootChance: Double
        let dwellTimeRange: ClosedRange<TimeInterval>
        let fittsLawA: Double // Fitts' Law coefficient A
        let fittsLawB: Double // Fitts' Law coefficient B
        let tremorIntensity: Double
        let handEyeDelay: ClosedRange<TimeInterval>
        let pathCurvature: Double // Tendency to create curved paths
        
        static let natural = MotionProfile(
            maxVelocity: 800.0,
            acceleration: 2000.0,
            jitterAmount: 2.0,
            overshootChance: 0.15,
            dwellTimeRange: 0.02...0.08,
            fittsLawA: 0.1,
            fittsLawB: 0.15,
            tremorIntensity: 0.5,
            handEyeDelay: 0.05...0.15,
            pathCurvature: 0.3
        )
        
        static let careful = MotionProfile(
            maxVelocity: 400.0,
            acceleration: 1200.0,
            jitterAmount: 1.0,
            overshootChance: 0.05,
            dwellTimeRange: 0.05...0.12,
            fittsLawA: 0.12,
            fittsLawB: 0.18,
            tremorIntensity: 0.3,
            handEyeDelay: 0.08...0.20,
            pathCurvature: 0.2
        )
        
        static let fast = MotionProfile(
            maxVelocity: 1200.0,
            acceleration: 3000.0,
            jitterAmount: 3.0,
            overshootChance: 0.25,
            dwellTimeRange: 0.01...0.04,
            fittsLawA: 0.08,
            fittsLawB: 0.12,
            tremorIntensity: 0.8,
            handEyeDelay: 0.03...0.10,
            pathCurvature: 0.4
        )
    }
    
    struct Point {
        let x: Double
        let y: Double
        let timestamp: TimeInterval
    }
    
    private let profile: MotionProfile
    private let mouse: MouseDriver
    
    init(mouse: MouseDriver, profile: MotionProfile = .natural) {
        self.mouse = mouse
        self.profile = profile
    }
    
    func moveTo(target: CGPoint, from current: CGPoint, targetWidth: Double = 20.0) {
        // Add hand-eye coordination delay before starting movement
        let handEyeDelay = TimeInterval.random(in: profile.handEyeDelay)
        Thread.sleep(forTimeInterval: handEyeDelay)
        
        let path = generateAdvancedPath(from: current, to: target, targetWidth: targetWidth)
        executePath(path)
    }
    
    private func generateAdvancedPath(from start: CGPoint, to end: CGPoint, targetWidth: Double) -> [Point] {
        let distance = sqrt(pow(end.x - start.x, 2) + pow(end.y - start.y, 2))
        let duration = calculateFittsLawDuration(distance: distance, targetWidth: targetWidth)
        
        // Generate Bézier curve control points for natural path curvature
        let controlPoints = generateBezierControlPoints(start: start, end: end)
        
        var points: [Point] = []
        let stepCount = max(Int(distance / 3), 15) // More steps for smoother motion
        
        for i in 0...stepCount {
            let t = Double(i) / Double(stepCount)
            let easedT = applyAdvancedEasing(t)
            
            // Calculate position along Bézier curve
            var position = calculateBezierPoint(t: easedT, 
                                              p0: start, 
                                              p1: controlPoints.0, 
                                              p2: controlPoints.1, 
                                              p3: end)
            
            // Add natural jitter and micro-tremor
            if i > 0 && i < stepCount {
                position = addNaturalNoise(to: position, progress: easedT)
            }
            
            let timestamp = duration * t
            points.append(Point(x: position.x, y: position.y, timestamp: timestamp))
        }
        
        // Add micro-adjustments near target (settle behavior)
        points.append(contentsOf: generateSettleBehavior(target: end))
        
        // Add multi-step overshoot correction if applicable
        if Double.random(in: 0...1) < profile.overshootChance {
            points.append(contentsOf: generateAdvancedOvershoot(from: end, originalTarget: end))
        }
        
        return points
    }
    
    private func calculateFittsLawDuration(distance: Double, targetWidth: Double) -> TimeInterval {
        // Proper Fitts' Law: T = a + b * log2(D/W + 1)
        // Where D is distance, W is target width
        let difficultyIndex = log2(distance / targetWidth + 1)
        let baseDuration = profile.fittsLawA + profile.fittsLawB * difficultyIndex
        
        // Add natural variation (±15%)
        let variation = Double.random(in: 0.85...1.15)
        return TimeInterval(baseDuration * variation)
    }
    
    private func generateBezierControlPoints(start: CGPoint, end: CGPoint) -> (CGPoint, CGPoint) {
        let dx = end.x - start.x
        let dy = end.y - start.y
        let distance = sqrt(dx * dx + dy * dy)
        
        // Generate natural curve control points
        let curvatureAmount = profile.pathCurvature * distance * 0.2
        let angle1 = atan2(dy, dx) + .pi * 0.25 * Double.random(in: -1...1)
        let angle2 = atan2(dy, dx) - .pi * 0.25 * Double.random(in: -1...1)
        
        let control1 = CGPoint(
            x: start.x + dx * 0.33 + Darwin.cos(angle1) * curvatureAmount,
            y: start.y + dy * 0.33 + Darwin.sin(angle1) * curvatureAmount
        )
        
        let control2 = CGPoint(
            x: start.x + dx * 0.66 + Darwin.cos(angle2) * curvatureAmount,
            y: start.y + dy * 0.66 + Darwin.sin(angle2) * curvatureAmount
        )
        
        return (control1, control2)
    }
    
    private func calculateBezierPoint(t: Double, p0: CGPoint, p1: CGPoint, p2: CGPoint, p3: CGPoint) -> CGPoint {
        let u = 1 - t
        let tt = t * t
        let uu = u * u
        let uuu = uu * u
        let ttt = tt * t
        
        let x = uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x
        let y = uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y
        
        return CGPoint(x: x, y: y)
    }
    
    private func addNaturalNoise(to point: CGPoint, progress: Double) -> CGPoint {
        // Combine jitter and tremor for natural imperfection
        let jitter = Double.random(in: -profile.jitterAmount...profile.jitterAmount)
        let tremorX = Darwin.sin(progress * .pi * 8) * profile.tremorIntensity * Double.random(in: 0.5...1.0)
        let tremorY = Darwin.cos(progress * .pi * 6) * profile.tremorIntensity * Double.random(in: 0.5...1.0)
        
        return CGPoint(
            x: point.x + jitter + tremorX,
            y: point.y + jitter + tremorY
        )
    }
    
    private func generateSettleBehavior(target: CGPoint) -> [Point] {
        // Add small micro-adjustments as humans settle on target
        var settlePoints: [Point] = []
        let settleCount = Int.random(in: 1...3)
        
        for i in 0..<settleCount {
            let microX = target.x + Double.random(in: -0.5...0.5)
            let microY = target.y + Double.random(in: -0.5...0.5)
            let settleTime = 0.01 + Double(i) * 0.005
            
            settlePoints.append(Point(x: microX, y: microY, timestamp: settleTime))
        }
        
        return settlePoints
    }
    
    private func applyAdvancedEasing(_ t: Double) -> Double {
        // Multi-stage easing with natural acceleration patterns
        if t < 0.1 {
            // Slow start (hand activation)
            return 2 * t * t
        } else if t < 0.7 {
            // Acceleration phase
            return easeInOutCubic((t - 0.1) / 0.6) * 0.8 + 0.02
        } else {
            // Deceleration phase (target approach)
            let localT = (t - 0.7) / 0.3
            return 0.82 + 0.18 * (1 - (1 - localT) * (1 - localT))
        }
    }
    
    private func easeInOutCubic(_ t: Double) -> Double {
        return t < 0.5 ? 4 * t * t * t : 1 - pow(-2 * t + 2, 3) / 2
    }
    
    private func generateAdvancedOvershoot(from point: CGPoint, originalTarget: CGPoint) -> [Point] {
        // Multi-step overshoot with realistic correction pattern
        let overshootDistance = Double.random(in: 8...25)
        let angle = atan2(originalTarget.y - point.y, originalTarget.x - point.x) + 
                   Double.random(in: -0.3...0.3) // Slight angle deviation
        
        let overshootX = point.x + Darwin.cos(angle) * overshootDistance
        let overshootY = point.y + Darwin.sin(angle) * overshootDistance
        
        // Multi-step correction (humans don't correct in one movement)
        var correctionPoints: [Point] = []
        
        // Initial overshoot
        correctionPoints.append(Point(x: overshootX, y: overshootY, timestamp: 0.02))
        
        // Correction steps with diminishing error
        let correctionSteps = Int.random(in: 2...4)
        for i in 1...correctionSteps {
            let progress = Double(i) / Double(correctionSteps)
            let errorReduction = pow(1 - progress, 2) // Quadratic error reduction
            
            let correctionX = overshootX + (originalTarget.x - overshootX) * progress + 
                             Double.random(in: -2...2) * errorReduction
            let correctionY = overshootY + (originalTarget.y - overshootY) * progress + 
                             Double.random(in: -2...2) * errorReduction
            
            let stepTime = 0.02 + Double(i) * 0.015
            correctionPoints.append(Point(x: correctionX, y: correctionY, timestamp: stepTime))
        }
        
        return correctionPoints
    }
    
    private func executePath(_ path: [Point]) {
        var lastPoint = path[0]
        var lastTime = CACurrentMediaTime()
        
        for point in path.dropFirst() {
            let deltaX = Int(point.x - lastPoint.x)
            let deltaY = Int(point.y - lastPoint.y)
            
            // Wait for proper timing
            let targetTime = lastTime + point.timestamp - lastPoint.timestamp
            let currentTime = CACurrentMediaTime()
            if targetTime > currentTime {
                Thread.sleep(forTimeInterval: targetTime - currentTime)
            }
            
            // Send mouse movement
            if deltaX != 0 || deltaY != 0 {
                mouse.moveDelta(deltaX, deltaY)
            }
            
            lastPoint = point
            lastTime = CACurrentMediaTime()
        }
        
        // Add final dwell time
        let dwellTime = TimeInterval.random(in: profile.dwellTimeRange)
        Thread.sleep(forTimeInterval: dwellTime)
    }
}
