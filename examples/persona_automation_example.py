#!/usr/bin/env python3
"""
BrowserGeist Persona System Example

Demonstrates how to use realistic user personas for automation
that mimics specific types of computer users.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from browsergeist import HumanMouse, automation_session, list_personas
from user_personas import get_persona_summary
import time


def demonstrate_persona_differences():
    """Demonstrate the differences between personas"""
    print("🎭 BrowserGeist Persona System Demo")
    print("=" * 60)
    
    # Show available personas
    print("📋 Available User Personas:")
    summaries = get_persona_summary()
    for name, description in summaries.items():
        print(f"   • {name}: {description}")
    
    print("\n🧪 Demonstrating Persona Behaviors:")
    print("-" * 60)
    
    # Demonstrate each persona
    for persona_name in ["tech_professional", "casual_user", "senior_user"]:
        print(f"\n👤 {persona_name.replace('_', ' ').title()}:")
        
        try:
            # Create bot with specific persona
            with automation_session(persona=persona_name, command_timeout=10.0) as bot:
                
                # Get persona characteristics
                persona_info = bot.get_current_persona()
                if persona_info:
                    print(f"   📊 Experience Level: {persona_info['experience_level']}")
                    print(f"   📊 Current Energy: {persona_info['current_energy']:.2f}")
                    print(f"   📊 Current Focus: {persona_info['current_focus']:.2f}")
                    
                    # Demonstrate mouse movement (different speeds/precision)
                    print(f"   🖱️  Demonstrating mouse movement...")
                    start_time = time.time()
                    result = bot.move_to((200, 200))
                    movement_time = time.time() - start_time
                    print(f"       Movement completed in {movement_time:.3f}s")
                    
                    # Demonstrate typing (different speeds/styles)
                    print(f"   ⌨️  Demonstrating typing...")
                    start_time = time.time()
                    result = bot.type_text("Hello, this is automated typing!")
                    typing_time = time.time() - start_time
                    print(f"       Typing completed in {typing_time:.3f}s")
                    
                    # Show persona state after activity
                    bot.update_persona_state()
                    updated_info = bot.get_current_persona()
                    print(f"   📈 Energy after activity: {updated_info['current_energy']:.2f}")
                    print(f"   📈 Focus after activity: {updated_info['current_focus']:.2f}")
                    
                else:
                    print(f"   ❌ Could not get persona information")
                    
        except Exception as e:
            print(f"   ⚠️  Demo failed (daemon not running): {type(e).__name__}")


def automation_workflow_example():
    """Example of persona-aware automation workflow"""
    print(f"\n🚀 Persona-Aware Automation Workflow Example")
    print("-" * 60)
    
    # Example: Different personas filling out a form
    form_data = {
        "name": "John Doe",
        "email": "john.doe@example.com", 
        "message": "This is a test message for the contact form."
    }
    
    for persona_name in ["tech_professional", "casual_user", "senior_user"]:
        print(f"\n👤 {persona_name.replace('_', ' ').title()} filling out form:")
        
        try:
            with automation_session(persona=persona_name) as bot:
                print(f"   1. Navigate to name field...")
                # bot.move_to("name_field.png")  # Would find name field
                # bot.click()
                
                print(f"   2. Type name with {persona_name} characteristics...")
                # bot.type_text(form_data["name"])
                
                print(f"   3. Navigate to email field...")
                # bot.move_to("email_field.png")
                # bot.click()
                
                print(f"   4. Type email...")
                # bot.type_text(form_data["email"])
                
                print(f"   5. Navigate to message field...")
                # bot.move_to("message_field.png")
                # bot.click()
                
                print(f"   6. Type message...")
                # bot.type_text(form_data["message"])
                
                print(f"   7. Submit form...")
                # bot.move_to("submit_button.png")
                # bot.click()
                
                # Get final persona state
                persona_info = bot.get_current_persona()
                if persona_info:
                    print(f"   📊 Final state - Energy: {persona_info['current_energy']:.2f}, Focus: {persona_info['current_focus']:.2f}")
                
        except Exception as e:
            print(f"   ⚠️  Workflow simulation (daemon required for actual automation)")


def persona_comparison_demo():
    """Compare the three personas side by side"""
    print(f"\n📊 Persona Comparison Demo")
    print("-" * 60)
    
    # Get all personas for comparison
    from user_personas import PERSONAS
    
    print("\n🏃‍♂️ Speed Comparison:")
    for name, persona in PERSONAS.items():
        mouse_speed = persona.mouse_behavior.base_speed
        typing_speed = persona.keyboard_behavior.base_wpm
        print(f"   {name:18s}: {mouse_speed:4.0f} px/s mouse, {typing_speed:2.0f} WPM typing")
    
    print("\n🎯 Precision & Error Rates:")
    for name, persona in PERSONAS.items():
        precision = persona.mouse_behavior.precision_level
        error_rate = persona.keyboard_behavior.error_rate
        print(f"   {name:18s}: {precision:.2f} precision, {error_rate:.1%} error rate")
    
    print("\n🧠 Cognitive Characteristics:")
    for name, persona in PERSONAS.items():
        decision_speed = persona.cognitive_behavior.decision_speed
        hesitation = persona.cognitive_behavior.hesitation_tendency
        print(f"   {name:18s}: {decision_speed:.1f}x decision speed, {hesitation:.1%} hesitation")
    
    print("\n⚡ Energy & Fatigue Simulation:")
    for name, persona in PERSONAS.items():
        # Simulate some activity
        persona.accumulate_fatigue(60.0)  # 1 hour session
        adjusted_mouse = persona.get_adjusted_mouse_speed()
        adjusted_typing = persona.get_adjusted_typing_speed()
        print(f"   {name:18s}: {adjusted_mouse:4.0f} px/s mouse, {adjusted_typing:2.0f} WPM (after 1 hour)")


def main():
    """Main demonstration"""
    print("🎭 BrowserGeist User Personas - Complete Demo")
    print("=" * 60)
    print("""
This demo showcases the BrowserGeist persona system which simulates
three distinct types of computer users with realistic behavioral patterns:

• Tech Professional (Alex Chen): Fast, precise, confident
• Casual User (Sarah Johnson): Moderate speed, occasional hesitation  
• Senior User (Robert Williams): Careful, deliberate, methodical

Each persona has unique characteristics for:
- Mouse movement speed and precision
- Typing speed and error patterns
- Decision-making and hesitation tendencies
- Fatigue accumulation over time
""")
    
    demonstrate_persona_differences()
    persona_comparison_demo()
    automation_workflow_example()
    
    print(f"\n🎯 Usage in Your Automation Scripts:")
    print("-" * 60)
    print("""
# Use a specific persona for automation
with automation_session(persona="tech_professional") as bot:
    bot.move_to("login_button.png")  # Fast, precise movement
    bot.click()                      # Quick, confident click
    bot.type_text("username")        # Fast touch-typing

# Switch personas mid-session
bot.set_persona("senior_user")
bot.move_to("submit_button.png")     # Slower, more careful movement
bot.click()                          # Deliberate click with longer dwell time

# Get persona information
persona_info = bot.get_current_persona()
print(f"Current user: {persona_info['name']}")
print(f"Energy level: {persona_info['current_energy']}")
""")
    
    print(f"\n✅ Persona System Features:")
    print("-" * 60)
    print("   • Realistic behavioral modeling based on user research")
    print("   • Dynamic state management (energy, focus, fatigue)")
    print("   • Consistent patterns within persona constraints")
    print("   • Randomization that maintains persona characteristics")
    print("   • Production-ready for undetectable automation")


if __name__ == "__main__":
    main()
