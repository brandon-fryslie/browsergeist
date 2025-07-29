/**
 * macOS Accessibility API Integration
 * 
 * Provides undetectable element discovery using macOS Accessibility APIs
 * for natural browser automation targeting.
 */

import Foundation
import ApplicationServices
import CoreFoundation
import AppKit

class AccessibilityElementFinder {
    
    /**
     * Find UI elements by role (button, textfield, etc.)
     */
    static func findElementsByRole(_ role: String, in application: AXUIElement) -> [AXUIElement] {
        var elements: [AXUIElement] = []
        
        // Get all children of the application
        if let children = getChildren(of: application) {
            for child in children {
                findElementsRecursively(child, role: role, results: &elements)
            }
        }
        
        return elements
    }
    
    /**
     * Find UI elements by accessible name/title
     */
    static func findElementsByName(_ name: String, in application: AXUIElement) -> [AXUIElement] {
        var elements: [AXUIElement] = []
        
        if let children = getChildren(of: application) {
            for child in children {
                findElementsByNameRecursively(child, name: name, results: &elements)
            }
        }
        
        return elements
    }
    
    /**
     * Find text fields and input elements
     */
    static func findInputFields(in application: AXUIElement) -> [AXUIElement] {
        let inputRoles = ["AXTextField", "AXTextArea", "AXSecureTextField", "AXComboBox"]
        var allInputs: [AXUIElement] = []
        
        for role in inputRoles {
            let inputs = findElementsByRole(role, in: application)
            allInputs.append(contentsOf: inputs)
        }
        
        return allInputs
    }
    
    /**
     * Find buttons and clickable elements
     */
    static func findButtons(in application: AXUIElement) -> [AXUIElement] {
        let buttonRoles = ["AXButton", "AXLink", "AXMenuButton"]
        var allButtons: [AXUIElement] = []
        
        for role in buttonRoles {
            let buttons = findElementsByRole(role, in: application)
            allButtons.append(contentsOf: buttons)
        }
        
        return allButtons
    }
    
    /**
     * Get the frontmost application for browser targeting
     */
    static func getFrontmostApplication() -> AXUIElement? {
        let systemWideElement = AXUIElementCreateSystemWide()
        
        var frontmostApp: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(systemWideElement, kAXFocusedApplicationAttribute as CFString, &frontmostApp)
        
        if result == .success, let app = frontmostApp {
            return (app as! AXUIElement)
        }
        
        return nil
    }
    
    /**
     * Get application by bundle identifier (e.g., "com.apple.Safari")
     */
    static func getApplicationByBundleId(_ bundleId: String) -> AXUIElement? {
        let runningApps = NSWorkspace.shared.runningApplications
        
        for app in runningApps {
            if app.bundleIdentifier == bundleId {
                let pid = app.processIdentifier
                return AXUIElementCreateApplication(pid)
            }
        }
        
        return nil
    }
    
    /**
     * Get element position for clicking
     */
    static func getElementPosition(_ element: AXUIElement) -> CGPoint? {
        var position: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &position)
        
        if result == .success, let pos = position {
            var point = CGPoint.zero
            if AXValueGetValue(pos as! AXValue, .cgPoint, &point) {
                return point
            }
        }
        
        return nil
    }
    
    /**
     * Get element size
     */
    static func getElementSize(_ element: AXUIElement) -> CGSize? {
        var size: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &size)
        
        if result == .success, let sz = size {
            var cgSize = CGSize.zero
            if AXValueGetValue(sz as! AXValue, .cgSize, &cgSize) {
                return cgSize
            }
        }
        
        return nil
    }
    
    /**
     * Get element center point for clicking
     */
    static func getElementCenter(_ element: AXUIElement) -> CGPoint? {
        guard let position = getElementPosition(element),
              let size = getElementSize(element) else {
            return nil
        }
        
        return CGPoint(
            x: position.x + size.width / 2,
            y: position.y + size.height / 2
        )
    }
    
    /**
     * Get element title/name
     */
    static func getElementTitle(_ element: AXUIElement) -> String? {
        var title: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXTitleAttribute as CFString, &title)
        
        if result == .success, let titleString = title as? String {
            return titleString
        }
        
        // Try alternative attributes
        let alternativeAttributes = [kAXDescriptionAttribute, kAXHelpAttribute, kAXValueAttribute]
        
        for attribute in alternativeAttributes {
            var value: CFTypeRef?
            let altResult = AXUIElementCopyAttributeValue(element, attribute as CFString, &value)
            
            if altResult == .success, let valueString = value as? String, !valueString.isEmpty {
                return valueString
            }
        }
        
        return nil
    }
    
    /**
     * Get element role
     */
    static func getElementRole(_ element: AXUIElement) -> String? {
        var role: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXRoleAttribute as CFString, &role)
        
        if result == .success, let roleString = role as? String {
            return roleString
        }
        
        return nil
    }
    
    // MARK: - Private Helper Methods
    
    private static func getChildren(of element: AXUIElement) -> [AXUIElement]? {
        var children: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &children)
        
        if result == .success, let childrenArray = children as? [AXUIElement] {
            return childrenArray
        }
        
        return nil
    }
    
    private static func findElementsRecursively(_ element: AXUIElement, role: String, results: inout [AXUIElement]) {
        // Check if current element matches the role
        if let elementRole = getElementRole(element), elementRole == role {
            results.append(element)
        }
        
        // Recursively search children
        if let children = getChildren(of: element) {
            for child in children {
                findElementsRecursively(child, role: role, results: &results)
            }
        }
    }
    
    private static func findElementsByNameRecursively(_ element: AXUIElement, name: String, results: inout [AXUIElement]) {
        // Check if current element's title contains the name
        if let elementTitle = getElementTitle(element), 
           elementTitle.localizedCaseInsensitiveContains(name) {
            results.append(element)
        }
        
        // Recursively search children
        if let children = getChildren(of: element) {
            for child in children {
                findElementsByNameRecursively(child, name: name, results: &results)
            }
        }
    }
}

/**
 * High-level accessibility-based targeting for browser automation
 */
class AccessibilityTargeting {
    
    /**
     * Find and return coordinates for clicking a button by text
     */
    static func findButtonByText(_ text: String, bundleId: String? = nil) -> CGPoint? {
        let app = bundleId != nil ? 
            AccessibilityElementFinder.getApplicationByBundleId(bundleId!) :
            AccessibilityElementFinder.getFrontmostApplication()
        
        guard let application = app else { return nil }
        
        let buttons = AccessibilityElementFinder.findElementsByName(text, in: application)
        
        for button in buttons {
            if let role = AccessibilityElementFinder.getElementRole(button),
               ["AXButton", "AXLink", "AXMenuButton"].contains(role) {
                return AccessibilityElementFinder.getElementCenter(button)
            }
        }
        
        return nil
    }
    
    /**
     * Find input field by label text
     */
    static func findInputFieldByLabel(_ labelText: String, bundleId: String? = nil) -> CGPoint? {
        let app = bundleId != nil ? 
            AccessibilityElementFinder.getApplicationByBundleId(bundleId!) :
            AccessibilityElementFinder.getFrontmostApplication()
        
        guard let application = app else { return nil }
        
        // First try to find input fields with matching names
        let inputFields = AccessibilityElementFinder.findInputFields(in: application)
        
        for field in inputFields {
            if let title = AccessibilityElementFinder.getElementTitle(field),
               title.localizedCaseInsensitiveContains(labelText) {
                return AccessibilityElementFinder.getElementCenter(field)
            }
        }
        
        // Fallback: find labels and look for nearby input fields
        let labels = AccessibilityElementFinder.findElementsByName(labelText, in: application)
        
        for label in labels {
            if let labelPos = AccessibilityElementFinder.getElementPosition(label),
               let _ = AccessibilityElementFinder.getElementSize(label) {
                
                // Look for input fields near this label
                for field in inputFields {
                    if let fieldPos = AccessibilityElementFinder.getElementPosition(field) {
                        let distance = sqrt(pow(fieldPos.x - labelPos.x, 2) + pow(fieldPos.y - labelPos.y, 2))
                        
                        // If field is reasonably close to label (within 200 pixels)
                        if distance < 200 {
                            return AccessibilityElementFinder.getElementCenter(field)
                        }
                    }
                }
            }
        }
        
        return nil
    }
    
    /**
     * Find any clickable element by text content
     */
    static func findClickableElementByText(_ text: String, bundleId: String? = nil) -> CGPoint? {
        let app = bundleId != nil ? 
            AccessibilityElementFinder.getApplicationByBundleId(bundleId!) :
            AccessibilityElementFinder.getFrontmostApplication()
        
        guard let application = app else { return nil }
        
        let elements = AccessibilityElementFinder.findElementsByName(text, in: application)
        
        // Prioritize interactive elements
        let interactiveRoles = ["AXButton", "AXLink", "AXMenuButton", "AXMenuItem", "AXTab"]
        
        for element in elements {
            if let role = AccessibilityElementFinder.getElementRole(element),
               interactiveRoles.contains(role) {
                return AccessibilityElementFinder.getElementCenter(element)
            }
        }
        
        // Fallback to any element with the text
        if let firstElement = elements.first {
            return AccessibilityElementFinder.getElementCenter(firstElement)
        }
        
        return nil
    }
}
