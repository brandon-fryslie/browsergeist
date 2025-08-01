#!/usr/bin/env python3
"""
Facebook Account Creation Automation Example

Demonstrates comprehensive browser automation using BrowserGeist's natural
element targeting API. This example shows real-world usage including:
- Opening applications via Spotlight
- Menu navigation and window management
- Form filling with natural field targeting
- Multi-step workflow automation

This example is for educational purposes only and should be used responsibly
in accordance with Facebook's Terms of Service.
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, MotionProfiles, automation_session
from user_personas import get_persona


class FacebookSignupAutomation:
    """Automated Facebook account creation using natural browser targeting"""

    def __init__(self, use_persona=True, debug_mode=True):
        self.use_persona = use_persona
        self.debug_mode = debug_mode
        self.persona = get_persona("tech_professional") if use_persona else None

        # Account details to use for signup
        self.account_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "admin@vast.wang",
            "password": "SecurePassword123!",
            "birthday_month": "January",
            "birthday_day": "15",
            "birthday_year": "1990",
            "gender": "Male"
        }

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "STEP": "🔄"
        }
        emoji = level_emoji.get(level, "📝")
        print(f"[{timestamp}] {emoji} {message}")

    def wait_with_message(self, seconds: float, message: str):
        """Wait with user feedback"""
        self.log(f"{message} (waiting {seconds}s)")
        time.sleep(seconds)

    async def run_automation(self):
        """Execute the complete Facebook signup automation workflow"""
        self.log("🚀 Starting Facebook Signup Automation", "STEP")
        self.log("=" * 60)

        try:
            with automation_session(persona=self.persona) as bot:
                # Step 1: Open Safari via Spotlight
                await self.open_safari_via_spotlight(bot)

                # Step 2: Open private browsing window
                await self.open_private_window(bot)

                # Step 3: Navigate to Facebook
                await self.navigate_to_facebook(bot)

                # Step 4: Start account creation
                await self.start_account_creation(bot)

                # Step 5: Fill signup form
                await self.fill_signup_form(bot)

                # Step 6: Submit form (but stop before actual submission)
                await self.prepare_submission(bot)

                self.log("🎉 Automation completed successfully!", "SUCCESS")

        except Exception as e:
            self.log(f"Automation failed: {str(e)}", "ERROR")
            raise

    async def open_safari_via_spotlight(self, bot):
        """Open Safari browser using Spotlight search"""
        self.log("Opening Safari via Spotlight...", "STEP")

        try:
            # Open Spotlight with Cmd+Space
            self.log("Opening Spotlight (Cmd+Space)")
            bot._send_command({"action": "key_combination", "keys": ["cmd", "space"]})

            # Wait for Spotlight to open
            self.wait_with_message(1.5, "Waiting for Spotlight to open")

            # Type "Safari" to search for the application
            self.log("Typing 'Safari' in Spotlight")
            bot.type_text("Safari", delay_profile="fast", use_persona=True)

            # Wait for search results
            self.wait_with_message(1.0, "Waiting for search results")

            # Press Enter to open Safari
            self.log("Pressing Enter to launch Safari")
            bot._send_command({"action": "key_combination", "keys": ["return"]})

            # Wait for Safari to launch
            self.wait_with_message(3.0, "Waiting for Safari to launch")

            self.log("Safari opened successfully", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to open Safari: {e}", "ERROR")
            raise

    async def open_private_window(self, bot):
        """Open a new private browsing window"""
        self.log("Opening private browsing window...", "STEP")

        try:
            # Click on File menu
            self.log("Clicking File menu")
            try:
                bot.click_text("File", confidence=0.8, use_accessibility=True)
            except Exception:
                # Fallback: try different approaches
                self.log("Trying alternative File menu detection", "WARNING")
                bot.click_text("File", confidence=0.6, use_accessibility=False)

            # Wait for menu to open
            self.wait_with_message(1.0, "Waiting for File menu to open")

            # Click "New Private Window"
            self.log("Clicking 'New Private Window'")
            private_window_candidates = [
                "New Private Window",
                "Private Window",
                "New Incognito Window",
                "Private Browsing"
            ]

            success = False
            for candidate in private_window_candidates:
                try:
                    bot.click_text(candidate, confidence=0.7)
                    success = True
                    self.log(f"Found private window option: {candidate}")
                    break
                except Exception:
                    continue

            if not success:
                # Fallback: use keyboard shortcut
                self.log("Using keyboard shortcut for private window", "WARNING")
                bot._send_command({"action": "key_combination", "keys": ["cmd", "shift", "n"]})

            # Wait for private window to open
            self.wait_with_message(2.0, "Waiting for private window to open")

            self.log("Private browsing window opened", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to open private window: {e}", "ERROR")
            raise

    async def navigate_to_facebook(self, bot):
        """Navigate to Facebook.com"""
        self.log("Navigating to Facebook...", "STEP")

        try:
            # Click in the address bar
            self.log("Clicking address bar")
            address_bar_candidates = [
                "Address and Search",
                "Search or enter website name",
                "Enter URL",
                "www"
            ]

            # Try to find address bar naturally
            address_found = False
            for candidate in address_bar_candidates:
                try:
                    bot.click_text(candidate, confidence=0.6)
                    address_found = True
                    self.log(f"Found address bar using: {candidate}")
                    break
                except Exception:
                    continue

            if not address_found:
                # Fallback: use keyboard shortcut to focus address bar
                self.log("Using keyboard shortcut for address bar", "WARNING")
                bot._send_command({"action": "key_combination", "keys": ["cmd", "l"]})

            # Wait for address bar to be focused
            self.wait_with_message(1.0, "Waiting for address bar focus")

            # Type Facebook URL
            self.log("Typing facebook.com")
            bot.type_text("facebook.com", delay_profile="fast")

            # Press Enter to navigate
            self.log("Pressing Enter to navigate")
            bot._send_command({"action": "key_combination", "keys": ["return"]})

            # Wait for page to load
            self.wait_with_message(5.0, "Waiting for Facebook to load")

            self.log("Successfully navigated to Facebook", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to navigate to Facebook: {e}", "ERROR")
            raise

    async def start_account_creation(self, bot):
        """Click the 'Create new account' button"""
        self.log("Starting account creation process...", "STEP")

        try:
            # Look for account creation button/link
            create_account_candidates = [
                "Create new account",
                "Create New Account",
                "Sign up for Facebook",
                "Sign Up",
                "Create Account",
                "Join Facebook"
            ]

            success = False
            for candidate in create_account_candidates:
                try:
                    self.log(f"Looking for: {candidate}")
                    bot.click_text(candidate, confidence=0.7)
                    success = True
                    self.log(f"Found account creation option: {candidate}")
                    break
                except Exception as e:
                    self.log(f"Could not find '{candidate}': {e}", "WARNING")
                    continue

            if not success:
                raise Exception("Could not find account creation button")

            # Wait for signup form to load
            self.wait_with_message(3.0, "Waiting for signup form to load")

            self.log("Account creation form loaded", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to start account creation: {e}", "ERROR")
            raise

    async def fill_signup_form(self, bot):
        """Fill out the Facebook signup form"""
        self.log("Filling signup form...", "STEP")

        try:
            # Fill first name
            await self.fill_form_field(bot, "First name", self.account_data["first_name"])

            # Fill last name
            await self.fill_form_field(bot, "Last name", self.account_data["last_name"])

            # Fill email
            await self.fill_form_field(bot, "Email", self.account_data["email"])

            # Fill password
            await self.fill_form_field(bot, "Password", self.account_data["password"])

            # Handle birthday fields
            await self.fill_birthday_fields(bot)

            # Handle gender selection
            await self.select_gender(bot)

            self.log("Form filled successfully", "SUCCESS")

        except Exception as e:
            self.log(f"Failed to fill signup form: {e}", "ERROR")
            raise

    async def fill_form_field(self, bot, field_label: str, value: str):
        """Fill a specific form field with multiple candidate approaches"""
        self.log(f"Filling {field_label}: {value}")

        # Try multiple variations of field labels
        field_candidates = [
            field_label,
            field_label.lower(),
            field_label + " or phone number" if "email" in field_label.lower() else field_label,
            field_label + " (required)" if field_label else field_label
        ]

        success = False
        for candidate in field_candidates:
            try:
                bot.type_in_field(candidate, value, confidence=0.7, delay_profile="average")
                success = True
                self.log(f"Successfully filled {field_label} using label: {candidate}")
                break
            except Exception as e:
                self.log(f"Could not fill using '{candidate}': {e}", "WARNING")
                continue

        if not success:
            raise Exception(f"Could not fill field: {field_label}")

        # Small delay between fields for natural flow
        time.sleep(0.5)

    async def fill_birthday_fields(self, bot):
        """Handle birthday dropdowns/fields"""
        self.log("Filling birthday information")

        try:
            # Try to fill birthday fields - Facebook may use dropdowns or input fields
            birthday_fields = [
                ("Month", self.account_data["birthday_month"]),
                ("Day", self.account_data["birthday_day"]),
                ("Year", self.account_data["birthday_year"])
            ]

            for field_name, value in birthday_fields:
                try:
                    # Try as regular input field first
                    await self.fill_form_field(bot, field_name, value)
                except Exception:
                    # Try as dropdown
                    try:
                        bot.click_text(field_name, confidence=0.7)
                        time.sleep(1.0)
                        bot.click_text(value, confidence=0.7)
                        self.log(f"Selected {field_name}: {value} from dropdown")
                    except Exception as e:
                        self.log(f"Could not set {field_name}: {e}", "WARNING")

        except Exception as e:
            self.log(f"Birthday fields handling failed: {e}", "WARNING")

    async def select_gender(self, bot):
        """Select gender option"""
        self.log(f"Selecting gender: {self.account_data['gender']}")

        try:
            gender_candidates = [
                self.account_data["gender"],
                self.account_data["gender"].lower(),
                "Male" if self.account_data["gender"] == "Male" else "Female"
            ]

            for candidate in gender_candidates:
                try:
                    bot.click_text(candidate, confidence=0.7)
                    self.log(f"Selected gender: {candidate}")
                    break
                except Exception:
                    continue

        except Exception as e:
            self.log(f"Gender selection failed: {e}", "WARNING")

    async def prepare_submission(self, bot):
        """Prepare for form submission (but don't actually submit)"""
        self.log("Preparing form submission...", "STEP")

        try:
            # Look for submit button but don't click it
            submit_candidates = [
                "Sign Up",
                "Create Account",
                "Join Facebook",
                "Get Started"
            ]

            for candidate in submit_candidates:
                try:
                    # Just find the button, don't click
                    screenshot = bot._take_screenshot()
                    if screenshot is not None:
                        result = bot.vision.find_text(screenshot, candidate, confidence=0.7)
                        if result:
                            self.log(f"Found submit button: {candidate}")
                            self.log("⚠️  Form is ready for submission but stopping here for safety", "WARNING")
                            self.log("⚠️  Manual review recommended before actual account creation", "WARNING")
                            return
                except Exception:
                    continue

            self.log("Submit button location identified", "SUCCESS")

        except Exception as e:
            self.log(f"Form preparation failed: {e}", "WARNING")


async def main():
    """Main execution function"""
    print("🌐 Facebook Account Creation Automation")
    print("=" * 50)
    print()
    print("⚠️  IMPORTANT NOTICE:")
    print("   This example is for educational purposes only.")
    print("   Please ensure compliance with Facebook's Terms of Service.")
    print("   The automation will stop before actual account submission.")
    print()

    # Ask for user confirmation
    response = input("Do you want to proceed with the automation demo? (y/N): ")
    if response.lower() != 'y':
        print("Automation cancelled by user.")
        return

    print("\n🚀 Starting automation in 3 seconds...")
    time.sleep(3)

    # Create and run automation
    automation = FacebookSignupAutomation(use_persona=True, debug_mode=True)

    try:
        await automation.run_automation()

        print("\n" + "=" * 50)
        print("✅ Automation demonstration completed successfully!")
        print()
        print("📋 What was demonstrated:")
        print("  ✓ Spotlight application launching")
        print("  ✓ Menu navigation and window management")
        print("  ✓ Natural element targeting (text-based)")
        print("  ✓ Form field detection and filling")
        print("  ✓ Multi-candidate element finding")
        print("  ✓ Keyboard shortcuts and key combinations")
        print("  ✓ Accessibility API integration")
        print("  ✓ Human-like typing and movement patterns")
        print()
        print("🔧 BrowserGeist Features Used:")
        print("  • Natural element targeting API")
        print("  • macOS Accessibility integration")
        print("  • Human motion simulation")
        print("  • Multi-method element detection")
        print("  • Comprehensive error handling")
        print("  • User persona behavioral adaptation")

    except KeyboardInterrupt:
        print("\n⚠️  Automation interrupted by user")
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        print("   Check that Safari is installed and accessible")
        print("   Ensure proper permissions are granted")


if __name__ == "__main__":
    asyncio.run(main())
