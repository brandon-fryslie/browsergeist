import Foundation
import CoreGraphics
import ImageIO
import ScreenCaptureKit
import UniformTypeIdentifiers

/**
 * Screen Capture Module
 * 
 * Modern ScreenCaptureKit-based screen capture for vision processing
 * with support for region-based capture and multiple displays.
 * Compatible with macOS 15+ requirements.
 */
@available(macOS 12.3, *)
class ScreenCapture {
    
    struct CaptureRegion {
        let x: CGFloat
        let y: CGFloat
        let width: CGFloat
        let height: CGFloat
        
        var rect: CGRect {
            return CGRect(x: x, y: y, width: width, height: height)
        }
    }
    
    enum CaptureError: Error {
        case captureFailure
        case imageCreationFailure
        case dataConversionFailure
        case permissionDenied
        case noDisplaysAvailable
    }
    
    private static var cachedContent: SCShareableContent?
    private static var lastContentUpdate: Date?
    private static let contentCacheInterval: TimeInterval = 5.0 // Cache for 5 seconds
    
    static func captureFullScreen() async throws -> CGImage {
        // Get shareable content (cached for performance)
        let content = try await getShareableContent()
        
        guard let mainDisplay = content.displays.first else {
            throw CaptureError.noDisplaysAvailable
        }
        
        // Create configuration for full screen capture
        let config = SCStreamConfiguration()
        config.width = Int(mainDisplay.frame.width)
        config.height = Int(mainDisplay.frame.height)
        config.capturesAudio = false
        config.shouldBeOpaque = true
        config.pixelFormat = kCVPixelFormatType_32BGRA
        
        // Create filter with the main display
        let filter = SCContentFilter(display: mainDisplay, excludingWindows: [])
        
        // Capture the screenshot
        let sample = try await SCScreenshotManager.captureImage(
            contentFilter: filter,
            configuration: config
        )
        
        return sample
    }
    
    // Simplified synchronous screen capture using CGDisplayCreateImage alternative
    // This uses a different approach that should work on macOS 15+
    static func captureFullScreenLegacy() throws -> CGImage {
        // Get screen dimensions
        let screenRect = CGDisplayBounds(CGMainDisplayID())
        
        // Create image context (unused - legacy function)
        guard CGContext(
            data: nil,
            width: Int(screenRect.width),
            height: Int(screenRect.height),
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        ) != nil else {
            throw CaptureError.captureFailure
        }
        
        // This is a workaround - we'll capture using window list without the deprecated function
        // For now, throw an error to force using ScreenCaptureKit
        throw CaptureError.captureFailure
    }
    
    static func getShareableContent() async throws -> SCShareableContent {
        // Use cached content if available and fresh
        if let cachedContent = cachedContent,
           let lastUpdate = lastContentUpdate,
           Date().timeIntervalSince(lastUpdate) < contentCacheInterval {
            return cachedContent
        }
        
        // Get fresh content
        let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
        
        // Cache the content
        cachedContent = content
        lastContentUpdate = Date()
        
        return content
    }
    
    static func captureRegion(_ region: CaptureRegion) async throws -> CGImage {
        let fullScreenImage = try await captureFullScreen()
        
        guard let croppedImage = fullScreenImage.cropping(to: region.rect) else {
            throw CaptureError.imageCreationFailure
        }
        
        return croppedImage
    }
    
    // Legacy synchronous version for backward compatibility
    static func captureRegionSync(_ region: CaptureRegion) throws -> CGImage {
        let fullScreenImage = try captureFullScreenLegacy()
        
        guard let croppedImage = fullScreenImage.cropping(to: region.rect) else {
            throw CaptureError.imageCreationFailure
        }
        
        return croppedImage
    }
    
    static func imageToData(_ image: CGImage, format: String = "png") throws -> Data {
        let mutableData = CFDataCreateMutable(nil, 0)!
        
        let uti: UTType
        switch format.lowercased() {
        case "jpg", "jpeg":
            uti = .jpeg
        case "png":
            uti = .png
        default:
            uti = .png
        }
        
        guard let destination = CGImageDestinationCreateWithData(mutableData, uti.identifier as CFString, 1, nil) else {
            throw CaptureError.dataConversionFailure
        }
        
        CGImageDestinationAddImage(destination, image, nil)
        
        if !CGImageDestinationFinalize(destination) {
            throw CaptureError.dataConversionFailure
        }
        
        return mutableData as Data
    }
    
    static func getScreenDimensions() -> CGSize {
        guard let mainDisplay = CGDisplayBounds(CGMainDisplayID()) as CGRect? else {
            return CGSize.zero
        }
        return mainDisplay.size
    }
    
    static func getAllDisplays() -> [CGDirectDisplayID] {
        var displayCount: UInt32 = 0
        CGGetActiveDisplayList(0, nil, &displayCount)
        
        var displays = [CGDirectDisplayID](repeating: 0, count: Int(displayCount))
        CGGetActiveDisplayList(displayCount, &displays, &displayCount)
        
        return displays
    }
    
    // Synchronous wrapper that uses a simple approach for immediate needs
    static func captureFullScreenSync() throws -> CGImage {
        // For now, we'll create a simple fallback that creates a test image
        // In a real implementation, we'd need to restructure the daemon to support async calls
        // or use a different capture method
        
        // Create a simple test image for development
        let screenRect = CGDisplayBounds(CGMainDisplayID())
        let width = Int(screenRect.width)
        let height = Int(screenRect.height)
        
        guard let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        ) else {
            throw CaptureError.captureFailure
        }
        
        // Fill with a solid color for testing
        context.setFillColor(CGColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 1.0))
        context.fill(CGRect(x: 0, y: 0, width: width, height: height))
        
        guard let image = context.makeImage() else {
            throw CaptureError.imageCreationFailure
        }
        
        return image
    }
}
