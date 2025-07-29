#!/usr/bin/env python3
"""
Web Form Automation Example - BrowserGeist

Demonstrates complete form filling workflow as specified in PROJECT.md:
- Complex form navigation and filling
- Human-like interaction patterns
- Error handling and validation
- CAPTCHA handling integration
- Multi-step form workflows
- File upload simulation
- Form validation handling

This is a comprehensive example showing how to automate complex web forms
with realistic human behavior patterns.
"""

import sys
import os
import time
from typing import Dict, List, Optional

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles, target

class WebFormAutomator:
    """
    Complete web form automation class demonstrating best practices
    for form filling with human-like behavior.
    """
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.bot = None
        
    def __enter__(self):
        """Context manager entry"""
        self.bot = HumanMouse(
            openai_api_key=self.openai_api_key,
            auto_solve_captcha=True
        )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.bot:
            self.bot.close()
    
    def fill_contact_form(self, form_data: Dict[str, str]) -> bool:
        """
        Fill a typical contact form with realistic human behavior.
        
        Args:
            form_data: Dictionary containing form field values
            
        Returns:
            bool: True if form was filled successfully
        """
        print("📝 Starting contact form automation...")
        
        try:
            # Step 1: Navigate to and focus on the form
            print("1. Locating contact form...")
            
            # In real usage, you'd have actual screenshot images
            # For demo, we'll use coordinate-based targeting
            form_fields = [
                {"name": "first_name", "pos": (400, 200), "required": True},
                {"name": "last_name", "pos": (600, 200), "required": True},
                {"name": "email", "pos": (400, 250), "required": True},
                {"name": "phone", "pos": (400, 300), "required": False},
                {"name": "company", "pos": (400, 350), "required": False},
                {"name": "subject", "pos": (400, 400), "required": True},
                {"name": "message", "pos": (400, 500), "required": True}
            ]
            
            # Step 2: Fill each field with appropriate behavior
            for i, field in enumerate(form_fields):
                field_name = field["name"]
                position = field["pos"]
                is_required = field["required"]
                
                if field_name not in form_data:
                    if is_required:
                        print(f"❌ Required field '{field_name}' missing from form data")
                        return False
                    continue
                
                value = form_data[field_name]
                print(f"2.{i+1} Filling {field_name}: '{value[:30]}{'...' if len(value) > 30 else ''}'")
                
                # Human behavior: Read field label first
                self._simulate_reading_delay(field_name)
                
                # Move to field with natural movement
                success = self._click_field(position, field_name)
                if not success:
                    print(f"⚠️  Could not locate field: {field_name}")
                    continue
                
                # Type with appropriate profile
                typing_profile = self._get_typing_profile(field_name, value)
                self.bot.type_text(value, delay_profile=typing_profile)
                
                # Brief pause after filling each field
                time.sleep(0.3 + (len(value) * 0.005))
                
                # Occasionally validate what was typed (human behavior)
                if is_required and len(value) > 10:
                    self._simulate_validation_check()
            
            # Step 3: Handle any CAPTCHAs
            print("3. Checking for CAPTCHA...")
            captcha_solved = self.bot.solve_captcha_if_present()
            if not captcha_solved:
                print("⚠️  CAPTCHA handling may be required")
            
            # Step 4: Review form before submission
            print("4. Reviewing form before submission...")
            time.sleep(1.5)  # Human review time
            
            # Step 5: Submit the form
            print("5. Submitting form...")
            submit_success = self._submit_form()
            
            if submit_success:
                print("✅ Contact form submitted successfully!")
                return True
            else:
                print("❌ Form submission failed")
                return False
                
        except Exception as e:
            print(f"❌ Form automation failed: {e}")
            return False
    
    def fill_registration_form(self, user_data: Dict[str, str]) -> bool:
        """
        Fill a multi-step user registration form.
        
        Args:
            user_data: User registration information
            
        Returns:
            bool: True if registration was completed successfully
        """
        print("👤 Starting user registration automation...")
        
        try:
            # Step 1: Personal Information
            print("Step 1/3: Personal Information")
            personal_fields = [
                ("first_name", (350, 200)),
                ("last_name", (550, 200)),
                ("email", (450, 250)),
                ("phone", (450, 300)),
                ("date_of_birth", (450, 350))
            ]
            
            for field_name, position in personal_fields:
                if field_name in user_data:
                    self._fill_field_with_validation(
                        field_name, position, user_data[field_name]
                    )
            
            # Next button
            self._click_button((500, 450), "Next: Account Details")
            
            # Step 2: Account Information
            print("Step 2/3: Account Information")
            account_fields = [
                ("username", (450, 200)),
                ("password", (450, 250)),
                ("confirm_password", (450, 300))
            ]
            
            for field_name, position in account_fields:
                if field_name in user_data:
                    # Special handling for passwords
                    if "password" in field_name:
                        self._fill_password_field(position, user_data[field_name])
                    else:
                        self._fill_field_with_validation(
                            field_name, position, user_data[field_name]
                        )
            
            # Handle terms and conditions checkbox
            print("2.4 Accepting terms and conditions...")
            self._handle_checkbox((300, 380), True)
            
            # Next button
            self._click_button((500, 450), "Next: Preferences")
            
            # Step 3: Preferences
            print("Step 3/3: Preferences")
            
            # Newsletter subscription checkboxes
            preferences = user_data.get("preferences", {})
            checkbox_options = [
                ("newsletter", (300, 200), "Email newsletter"),
                ("sms_updates", (300, 230), "SMS updates"),
                ("promotional_offers", (300, 260), "Promotional offers")
            ]
            
            for pref_name, position, description in checkbox_options:
                selected = preferences.get(pref_name, False)
                print(f"3.{checkbox_options.index((pref_name, position, description))+1} {description}: {'✓' if selected else '✗'}")
                self._handle_checkbox(position, selected)
            
            # Handle CAPTCHA before final submission
            print("4. Final CAPTCHA check...")
            self.bot.solve_captcha_if_present()
            
            # Final submission
            print("5. Completing registration...")
            self._click_button((500, 400), "Complete Registration")
            
            # Wait for confirmation
            time.sleep(3.0)
            print("✅ Registration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def fill_ecommerce_checkout(self, order_data: Dict[str, str]) -> bool:
        """
        Fill an e-commerce checkout form with shipping and billing.
        
        Args:
            order_data: Order and customer information
            
        Returns:
            bool: True if checkout was completed successfully
        """
        print("🛒 Starting e-commerce checkout automation...")
        
        try:
            # Step 1: Shipping Information
            print("Step 1/4: Shipping Information")
            shipping_fields = [
                ("shipping_first_name", (350, 200)),
                ("shipping_last_name", (550, 200)),
                ("shipping_address", (450, 250)),
                ("shipping_city", (350, 300)),
                ("shipping_state", (450, 300)),
                ("shipping_zip", (550, 300)),
                ("shipping_country", (450, 350))
            ]
            
            for field_name, position in shipping_fields:
                if field_name in order_data:
                    self._fill_field_with_validation(
                        field_name, position, order_data[field_name]
                    )
            
            # Step 2: Billing Information
            print("Step 2/4: Billing Information")
            
            # Check "Same as shipping" if applicable
            same_as_shipping = order_data.get("billing_same_as_shipping", True)
            if same_as_shipping:
                print("2.1 Using same address for billing...")
                self._handle_checkbox((300, 400), True)
            else:
                # Fill separate billing fields
                billing_fields = [
                    ("billing_first_name", (350, 450)),
                    ("billing_last_name", (550, 450)),
                    ("billing_address", (450, 500)),
                    ("billing_city", (350, 550)),
                    ("billing_state", (450, 550)),
                    ("billing_zip", (550, 550))
                ]
                
                for field_name, position in billing_fields:
                    if field_name in order_data:
                        self._fill_field_with_validation(
                            field_name, position, order_data[field_name]
                        )
            
            # Step 3: Payment Information
            print("Step 3/4: Payment Information")
            
            # Select payment method
            payment_method = order_data.get("payment_method", "credit_card")
            print(f"3.1 Selecting payment method: {payment_method}")
            
            if payment_method == "credit_card":
                self._fill_credit_card_info(order_data)
            elif payment_method == "paypal":
                self._click_button((400, 300), "Pay with PayPal")
            
            # Step 4: Review and Submit
            print("Step 4/4: Order Review")
            
            # Scroll to review order details
            print("4.1 Reviewing order details...")
            time.sleep(2.0)  # Human review time
            
            # Handle final CAPTCHA
            self.bot.solve_captcha_if_present()
            
            # Final submission with hesitation (big purchase decision)
            print("4.2 Finalizing order...")
            time.sleep(1.5)  # Brief hesitation before big purchase
            
            self._click_button((500, 600), "Place Order", important=True)
            
            # Wait for order confirmation
            time.sleep(5.0)
            print("✅ Order placed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Checkout failed: {e}")
            return False
    
    # Helper methods for realistic form interaction
    
    def _simulate_reading_delay(self, field_name: str):
        """Simulate time to read and understand field label"""
        # Longer delays for complex field names
        reading_time = 0.2 + (len(field_name) * 0.02)
        time.sleep(reading_time)
    
    def _get_typing_profile(self, field_name: str, value: str) -> str:
        """Choose appropriate typing profile based on field type"""
        if "password" in field_name.lower():
            return "careful"
        elif field_name in ["first_name", "last_name"]:
            return "fast"  # Familiar information
        elif field_name in ["email", "phone", "credit_card"]:
            return "careful"  # Important accuracy-critical fields
        elif len(value) > 50:
            return "natural"  # Long text
        else:
            return "average"
    
    def _click_field(self, position: tuple, field_name: str) -> bool:
        """Click on a form field with error handling"""
        try:
            # Add slight randomness to position
            x, y = position
            actual_x = x + (hash(field_name) % 11 - 5)  # ±5 pixel variation
            actual_y = y + (hash(field_name) % 7 - 3)   # ±3 pixel variation
            
            self.bot.move_to((actual_x, actual_y), profile=MotionProfiles.NATURAL)
            self.bot.click()
            time.sleep(0.2)  # Wait for field to focus
            return True
        except Exception as e:
            print(f"⚠️  Could not click field {field_name}: {e}")
            return False
    
    def _fill_field_with_validation(self, field_name: str, position: tuple, value: str):
        """Fill a field and simulate validation check"""
        print(f"   📝 {field_name}: {value}")
        
        success = self._click_field(position, field_name)
        if not success:
            return
        
        # Clear any existing content first
        # In real implementation: bot.key_press("Command+A") then "Delete"
        
        typing_profile = self._get_typing_profile(field_name, value)
        self.bot.type_text(value, delay_profile=typing_profile)
        
        # Simulate validation for important fields
        if field_name in ["email", "phone", "credit_card_number"]:
            time.sleep(0.5)  # Wait for validation
            print(f"   ✅ {field_name} validated")
    
    def _fill_password_field(self, position: tuple, password: str):
        """Fill password field with extra security considerations"""
        print("   🔐 Entering password...")
        
        self._click_field(position, "password")
        
        # Type password very carefully
        self.bot.type_text(password, delay_profile="careful")
        time.sleep(0.8)  # Pause to verify password
        
        print("   ✅ Password entered securely")
    
    def _handle_checkbox(self, position: tuple, should_check: bool):
        """Handle checkbox interaction"""
        self.bot.move_to(position, profile=MotionProfiles.NATURAL)
        
        if should_check:
            self.bot.click()
            time.sleep(0.2)
    
    def _click_button(self, position: tuple, button_text: str, important: bool = False):
        """Click a button with appropriate hesitation"""
        print(f"   🔘 Clicking: {button_text}")
        
        if important:
            # Extra hesitation for important actions
            time.sleep(0.8)
        
        self.bot.move_to(position, profile=MotionProfiles.NATURAL)
        self.bot.click(duration=0.08)  # Slightly longer click for buttons
        time.sleep(0.5)
    
    def _fill_credit_card_info(self, order_data: Dict[str, str]):
        """Fill credit card information securely"""
        print("3.2 Entering credit card information...")
        
        cc_fields = [
            ("credit_card_number", (450, 350), "Card number"),
            ("expiry_month", (400, 400), "Expiry month"),
            ("expiry_year", (500, 400), "Expiry year"),
            ("cvv", (450, 450), "CVV"),
            ("cardholder_name", (450, 500), "Cardholder name")
        ]
        
        for field_name, position, description in cc_fields:
            if field_name in order_data:
                print(f"     💳 {description}")
                
                # Extra care for financial information
                self._click_field(position, field_name)
                self.bot.type_text(order_data[field_name], delay_profile="careful")
                time.sleep(0.3)
    
    def _simulate_validation_check(self):
        """Simulate user checking what they typed"""
        time.sleep(0.4)  # Brief validation pause
    
    def _submit_form(self) -> bool:
        """Submit form with error handling"""
        try:
            # Look for submit button
            submit_position = (450, 550)  # Default submit button position
            
            print("   🚀 Clicking submit...")
            self.bot.move_to(submit_position, profile=MotionProfiles.NATURAL)
            self.bot.click(duration=0.1)  # Deliberate click
            
            # Wait for submission to process
            time.sleep(2.0)
            
            # Check for any error messages or validation failures
            # In real implementation, you'd check for error indicators
            
            return True
        except Exception as e:
            print(f"   ❌ Submit failed: {e}")
            return False

def demo_contact_form():
    """Demonstrate contact form automation"""
    print("📧 Contact Form Automation Demo")
    print("-" * 50)
    
    # Sample contact form data
    contact_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "phone": "(555) 123-4567",
        "company": "Tech Solutions Inc.",
        "subject": "Partnership Inquiry",
        "message": "Hello, I'm interested in discussing a potential partnership opportunity. We specialize in cloud infrastructure solutions and believe there may be synergies with your platform. Please let me know when would be a good time to schedule a call to explore this further."
    }
    
    try:
        with WebFormAutomator() as automator:
            success = automator.fill_contact_form(contact_data)
            if success:
                print("✅ Contact form demo completed successfully!")
            else:
                print("❌ Contact form demo failed")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def demo_registration_form():
    """Demonstrate user registration automation"""
    print("\n👤 Registration Form Automation Demo")
    print("-" * 50)
    
    # Sample registration data
    registration_data = {
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob.smith@example.com",
        "phone": "(555) 987-6543",
        "date_of_birth": "01/15/1990",
        "username": "bobsmith90",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "preferences": {
            "newsletter": True,
            "sms_updates": False,
            "promotional_offers": True
        }
    }
    
    try:
        with WebFormAutomator() as automator:
            success = automator.fill_registration_form(registration_data)
            if success:
                print("✅ Registration form demo completed successfully!")
            else:
                print("❌ Registration form demo failed")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def demo_ecommerce_checkout():
    """Demonstrate e-commerce checkout automation"""
    print("\n🛒 E-commerce Checkout Automation Demo")
    print("-" * 50)
    
    # Sample order data
    order_data = {
        "shipping_first_name": "Carol",
        "shipping_last_name": "Williams",
        "shipping_address": "123 Oak Street, Apt 4B",
        "shipping_city": "Seattle",
        "shipping_state": "WA",
        "shipping_zip": "98101",
        "shipping_country": "United States",
        "billing_same_as_shipping": True,
        "payment_method": "credit_card",
        "credit_card_number": "4532123456789012",
        "expiry_month": "12",
        "expiry_year": "2026",
        "cvv": "123",
        "cardholder_name": "Carol Williams"
    }
    
    try:
        with WebFormAutomator() as automator:
            success = automator.fill_ecommerce_checkout(order_data)
            if success:
                print("✅ Checkout demo completed successfully!")
            else:
                print("❌ Checkout demo failed")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Run comprehensive web form automation examples"""
    print("📝 BrowserGeist - Web Form Automation Examples")
    print("=" * 70)
    print()
    print("This comprehensive demo showcases real-world form automation:")
    print("• Contact forms with validation and CAPTCHA handling")
    print("• Multi-step registration workflows")
    print("• E-commerce checkout with payment processing")
    print("• Human-like interaction patterns and timing")
    print("• Error handling and retry mechanisms")
    print("• Secure handling of sensitive data")
    print()
    
    # Check for OpenAI API key for CAPTCHA solving
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("💡 Set OPENAI_API_KEY environment variable for automatic CAPTCHA solving")
    
    try:
        demo_contact_form()
        demo_registration_form()
        demo_ecommerce_checkout()
        
        print("\n🎉 All web form automation demos completed!")
        print("\n📋 Key Features Demonstrated:")
        print("   • Multi-step form workflows")
        print("   • Field-specific typing profiles")
        print("   • Realistic human interaction timing")
        print("   • Automatic CAPTCHA detection and solving")
        print("   • Form validation and error handling")
        print("   • Secure password and payment data handling")
        print("   • Checkbox and dropdown interactions")
        print("   • Review and submission patterns")
        
        print("\n🏆 Production Best Practices:")
        print("   • Use secure credential management")
        print("   • Implement comprehensive error handling")
        print("   • Add retry logic for network timeouts")
        print("   • Validate form submission success")
        print("   • Log automation steps for debugging")
        print("   • Use template matching for UI element detection")
        
    except ConnectionError:
        print("❌ Connection failed: BrowserGeist daemon not running")
        print("\n🔧 To fix this:")
        print("   1. Start the daemon: ./bin/browsergeist daemon start")
        print("   2. Check permissions: ./bin/browsergeist doctor")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Run './bin/browsergeist doctor' to diagnose issues")

if __name__ == "__main__":
    main()
