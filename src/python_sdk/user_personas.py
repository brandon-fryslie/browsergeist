"""
User Personas for Realistic Behavior Simulation

This module defines realistic user personas with distinct behavioral patterns
for mouse movement, clicking, typing, and interaction styles. Each persona
represents a different type of computer user with statistically accurate
behavior patterns derived from human-computer interaction research.
"""

import random
import time
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class TypingStyle(Enum):
    HUNT_AND_PECK = "hunt_and_peck"
    TOUCH_TYPING = "touch_typing"
    HYBRID = "hybrid"


class ExperienceLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


@dataclass
class MouseBehaviorProfile:
    """Mouse behavior characteristics for a persona"""
    
    # Movement characteristics
    base_speed: float  # pixels/second base speed
    speed_variance: float  # ±percentage variance in speed
    acceleration_preference: float  # how quickly they accelerate (0.5-2.0)
    
    # Precision characteristics  
    precision_level: float  # how precise they are (0.5-1.0)
    overshoot_tendency: float  # probability of overshooting targets
    correction_attempts: Tuple[int, int]  # min/max correction attempts
    
    # Timing characteristics
    click_duration_ms: Tuple[float, float]  # min/max click duration
    double_click_speed_ms: float  # time between double clicks
    dwell_time_ms: Tuple[float, float]  # pause before clicking
    
    # Path characteristics
    curvature_preference: float  # how curved their movements are
    micro_movements: bool  # whether they make micro-adjustments
    tremor_intensity: float  # hand tremor simulation intensity
    
    # Scrolling characteristics
    scroll_speed: float  # scroll wheel sensitivity
    scroll_precision: float  # how precisely they scroll
    scroll_pause_chance: float  # probability of pausing while scrolling


@dataclass  
class KeyboardBehaviorProfile:
    """Keyboard behavior characteristics for a persona"""
    
    # Typing speed characteristics
    base_wpm: float  # words per minute baseline
    wpm_variance: float  # ±percentage variance in WPM
    typing_style: TypingStyle  # hunt-and-peck, touch typing, or hybrid
    
    # Rhythm characteristics
    inter_key_delay_ms: Tuple[float, float]  # delay between keystrokes
    burst_typing: bool  # whether they type in bursts
    burst_length: Tuple[int, int]  # keys per burst if burst_typing
    burst_pause_ms: Tuple[float, float]  # pause between bursts
    
    # Error characteristics
    error_rate: float  # probability of making typing errors
    backspace_usage: float  # how often they use backspace vs retyping
    error_correction_delay_ms: Tuple[float, float]  # delay before correcting
    
    # Key press characteristics
    key_press_duration_ms: Tuple[float, float]  # how long keys are held
    key_overlap: bool  # whether they overlap key presses
    modifier_hold_style: str  # "brief" or "sustained" for ctrl/shift
    
    # Character-specific timing
    character_familiarity: Dict[str, float]  # speed multiplier per character
    common_bigrams: Dict[str, float]  # speed for common letter pairs
    
    # Thinking patterns
    thinking_pause_chance: float  # probability of pausing to think
    thinking_pause_ms: Tuple[float, float]  # duration of thinking pauses
    word_completion_pause_chance: float  # pause after completing words


@dataclass
class CognitiveBehaviorProfile:
    """Cognitive and decision-making characteristics"""
    
    # Decision making
    decision_speed: float  # how quickly they make choices (0.5-2.0)
    hesitation_tendency: float  # probability of hesitating before actions
    
    # Reading patterns
    reading_speed_wpm: float  # reading speed
    scanning_vs_reading: float  # probability of scanning vs careful reading
    
    # Multitasking
    attention_span_seconds: Tuple[float, float]  # how long they focus
    distraction_probability: float  # chance of getting distracted
    task_switching_delay_ms: Tuple[float, float]  # delay when switching focus
    
    # Error recovery
    error_detection_delay_ms: Tuple[float, float]  # time to notice errors
    patience_level: float  # how long they'll try before giving up
    
    # Interaction preferences
    prefers_keyboard_shortcuts: bool  # vs using mouse for everything
    comfort_with_right_click: float  # probability of using context menus
    scroll_vs_page_navigation: float  # preference for scrolling vs clicking


@dataclass
class UserPersona:
    """Complete user persona with all behavioral characteristics"""
    
    name: str
    description: str
    demographics: Dict[str, Any]
    experience_level: ExperienceLevel
    
    mouse_behavior: MouseBehaviorProfile
    keyboard_behavior: KeyboardBehaviorProfile
    cognitive_behavior: CognitiveBehaviorProfile
    
    # Session state (varies within persona constraints)
    current_energy_level: float = 1.0  # 0.5-1.5, affects speed/precision
    current_focus_level: float = 1.0   # 0.5-1.5, affects errors/hesitation
    fatigue_accumulation: float = 0.0  # increases over session
    
    def get_adjusted_mouse_speed(self) -> float:
        """Get current mouse speed adjusted for energy/focus"""
        base = self.mouse_behavior.base_speed
        variance = random.uniform(-self.mouse_behavior.speed_variance, 
                                 self.mouse_behavior.speed_variance)
        energy_factor = self.current_energy_level
        fatigue_factor = max(0.7, 1.0 - self.fatigue_accumulation * 0.1)
        
        return base * (1 + variance) * energy_factor * fatigue_factor
    
    def get_adjusted_typing_speed(self) -> float:
        """Get current typing speed adjusted for conditions"""
        base = self.keyboard_behavior.base_wpm
        variance = random.uniform(-self.keyboard_behavior.wpm_variance,
                                 self.keyboard_behavior.wpm_variance)
        focus_factor = self.current_focus_level
        fatigue_factor = max(0.8, 1.0 - self.fatigue_accumulation * 0.05)
        
        return base * (1 + variance) * focus_factor * fatigue_factor
    
    def accumulate_fatigue(self, session_duration_minutes: float):
        """Accumulate fatigue over session time"""
        # Different personas fatigue at different rates
        if self.experience_level == ExperienceLevel.EXPERT:
            fatigue_rate = 0.01  # Experts fatigue slower
        elif self.experience_level == ExperienceLevel.INTERMEDIATE:
            fatigue_rate = 0.015
        else:
            fatigue_rate = 0.02  # Beginners fatigue faster
            
        self.fatigue_accumulation = min(0.5, session_duration_minutes * fatigue_rate)
    
    def update_session_state(self):
        """Update energy and focus levels with natural variation"""
        # Energy varies more slowly
        self.current_energy_level += random.uniform(-0.05, 0.05)
        self.current_energy_level = max(0.5, min(1.5, self.current_energy_level))
        
        # Focus can change more rapidly
        self.current_focus_level += random.uniform(-0.1, 0.1)
        self.current_focus_level = max(0.5, min(1.5, self.current_focus_level))


# Define the three main personas
def create_tech_professional() -> UserPersona:
    """
    PERSONA 1: Tech Professional
    - Software developer/engineer, 28-35 years old
    - Expert computer user, touch typist
    - Fast, efficient, confident interactions
    - Uses keyboard shortcuts extensively
    """
    
    # Character familiarity for a programmer (faster with common code chars)
    char_familiarity = {
        'e': 1.2, 't': 1.2, 'a': 1.2, 'o': 1.2, 'i': 1.2, 'n': 1.2, 's': 1.2, 'r': 1.2,
        '{': 1.1, '}': 1.1, '(': 1.1, ')': 1.1, '[': 1.1, ']': 1.1, ';': 1.1, '=': 1.1,
        '"': 1.0, "'": 1.0, '<': 1.0, '>': 1.0, '/': 1.0, '\\': 1.0, '|': 1.0, '&': 1.0,
        'q': 0.9, 'z': 0.9, 'x': 0.9  # Less common letters
    }
    
    common_bigrams = {
        'th': 1.3, 'he': 1.3, 'in': 1.3, 'er': 1.3, 're': 1.3, 'an': 1.3,
        '()': 1.2, '{}': 1.2, '[]': 1.2, '==': 1.2, '!=': 1.2, '->': 1.2
    }
    
    return UserPersona(
        name="Alex Chen",
        description="Senior Software Engineer at tech company",
        demographics={
            "age": 32,
            "profession": "Software Engineer", 
            "computer_hours_daily": 10,
            "primary_os": "macOS",
            "years_programming": 8
        },
        experience_level=ExperienceLevel.EXPERT,
        
        mouse_behavior=MouseBehaviorProfile(
            base_speed=1200.0,  # Fast movement
            speed_variance=0.15,  # Consistent speed
            acceleration_preference=1.8,  # Quick acceleration
            precision_level=0.9,  # Very precise
            overshoot_tendency=0.05,  # Rarely overshoots
            correction_attempts=(1, 2),  # Quick corrections
            click_duration_ms=(45, 65),  # Quick clicks
            double_click_speed_ms=180,  # Fast double clicks
            dwell_time_ms=(20, 50),  # Minimal hesitation
            curvature_preference=0.2,  # Direct movements
            micro_movements=True,  # Fine adjustments
            tremor_intensity=0.3,  # Steady hands
            scroll_speed=1.3,  # Fast scrolling
            scroll_precision=0.9,  # Precise scrolling
            scroll_pause_chance=0.1  # Rarely pauses while scrolling
        ),
        
        keyboard_behavior=KeyboardBehaviorProfile(
            base_wpm=85,  # Fast typing
            wpm_variance=0.12,  # Consistent
            typing_style=TypingStyle.TOUCH_TYPING,
            inter_key_delay_ms=(40, 80),  # Rapid typing
            burst_typing=True,  # Types in bursts
            burst_length=(8, 15),  # Long bursts
            burst_pause_ms=(100, 300),  # Brief pauses
            error_rate=0.02,  # Very few errors
            backspace_usage=0.9,  # Corrects immediately
            error_correction_delay_ms=(50, 150),  # Quick corrections
            key_press_duration_ms=(50, 70),  # Quick key presses
            key_overlap=True,  # Smooth typing
            modifier_hold_style="sustained",  # Holds modifiers
            character_familiarity=char_familiarity,
            common_bigrams=common_bigrams,
            thinking_pause_chance=0.05,  # Rarely pauses to think
            thinking_pause_ms=(200, 800),  # Brief thinking
            word_completion_pause_chance=0.02  # Flows between words
        ),
        
        cognitive_behavior=CognitiveBehaviorProfile(
            decision_speed=1.8,  # Quick decisions
            hesitation_tendency=0.05,  # Confident
            reading_speed_wpm=350,  # Fast reader
            scanning_vs_reading=0.7,  # Prefers scanning
            attention_span_seconds=(300, 900),  # Long focus
            distraction_probability=0.1,  # Focused
            task_switching_delay_ms=(100, 300),  # Quick switching
            error_detection_delay_ms=(200, 500),  # Quick error detection
            patience_level=0.7,  # Moderately patient
            prefers_keyboard_shortcuts=True,  # Loves shortcuts
            comfort_with_right_click=0.9,  # Expert user
            scroll_vs_page_navigation=0.8  # Prefers scrolling
        )
    )


def create_casual_user() -> UserPersona:
    """
    PERSONA 2: Casual User
    - Marketing professional, 38-45 years old  
    - Intermediate computer skills, hybrid typist
    - Moderate speed, occasionally hesitant
    - Uses mix of mouse and keyboard
    """
    
    # Standard character familiarity for office worker
    char_familiarity = {
        'e': 1.1, 't': 1.1, 'a': 1.1, 'o': 1.1, 'i': 1.1, 'n': 1.1, 's': 1.1, 'r': 1.1,
        '@': 1.2, '.': 1.2, ',': 1.2, ' ': 1.2,  # Email/writing chars
        'q': 0.8, 'z': 0.8, 'x': 0.8, 'j': 0.8, 'k': 0.8  # Less familiar
    }
    
    common_bigrams = {
        'th': 1.2, 'he': 1.2, 'in': 1.2, 'er': 1.2, 're': 1.2, 'an': 1.2,
        'com': 1.3, '.com': 1.3, 'www': 1.2  # Web-related
    }
    
    return UserPersona(
        name="Sarah Johnson", 
        description="Marketing Manager with moderate computer experience",
        demographics={
            "age": 42,
            "profession": "Marketing Manager",
            "computer_hours_daily": 6,
            "primary_os": "macOS",
            "typing_education": "Some formal training"
        },
        experience_level=ExperienceLevel.INTERMEDIATE,
        
        mouse_behavior=MouseBehaviorProfile(
            base_speed=800.0,  # Moderate speed
            speed_variance=0.25,  # More variable
            acceleration_preference=1.2,  # Moderate acceleration
            precision_level=0.75,  # Good precision
            overshoot_tendency=0.15,  # Occasional overshoots
            correction_attempts=(1, 3),  # Sometimes needs multiple tries
            click_duration_ms=(60, 90),  # Deliberate clicks
            double_click_speed_ms=220,  # Slower double clicks
            dwell_time_ms=(50, 150),  # Some hesitation
            curvature_preference=0.4,  # Moderate curves
            micro_movements=True,  # Makes adjustments
            tremor_intensity=0.5,  # Average hand steadiness
            scroll_speed=1.0,  # Standard scrolling
            scroll_precision=0.7,  # Sometimes overshoots
            scroll_pause_chance=0.25  # Pauses to process content
        ),
        
        keyboard_behavior=KeyboardBehaviorProfile(
            base_wpm=55,  # Average typing speed
            wpm_variance=0.2,  # Variable speed
            typing_style=TypingStyle.HYBRID,
            inter_key_delay_ms=(80, 150),  # Moderate timing
            burst_typing=False,  # Steady typing
            burst_length=(4, 8),  # Shorter bursts when they occur
            burst_pause_ms=(200, 600),  # Longer pauses
            error_rate=0.05,  # Occasional errors
            backspace_usage=0.7,  # Usually corrects, sometimes retypes
            error_correction_delay_ms=(300, 800),  # Takes time to notice
            key_press_duration_ms=(65, 95),  # Deliberate presses
            key_overlap=False,  # More distinct keystrokes
            modifier_hold_style="brief",  # Quick modifier use
            character_familiarity=char_familiarity,
            common_bigrams=common_bigrams,
            thinking_pause_chance=0.15,  # Occasional thinking pauses
            thinking_pause_ms=(500, 1500),  # Longer thinking
            word_completion_pause_chance=0.08  # Pauses between words
        ),
        
        cognitive_behavior=CognitiveBehaviorProfile(
            decision_speed=1.0,  # Standard decision speed
            hesitation_tendency=0.2,  # Some hesitation
            reading_speed_wpm=250,  # Average reader
            scanning_vs_reading=0.4,  # Balanced approach
            attention_span_seconds=(180, 600),  # Moderate focus
            distraction_probability=0.2,  # Occasionally distracted
            task_switching_delay_ms=(300, 800),  # Takes time to refocus
            error_detection_delay_ms=(500, 1200),  # Takes time to notice errors
            patience_level=0.6,  # Moderately patient
            prefers_keyboard_shortcuts=False,  # Prefers mouse
            comfort_with_right_click=0.6,  # Sometimes uses context menus
            scroll_vs_page_navigation=0.5  # Uses both equally
        )
    )


def create_senior_user() -> UserPersona:
    """
    PERSONA 3: Senior User
    - Retired teacher, 65-72 years old
    - Beginner to intermediate skills, hunt-and-peck typist
    - Careful, deliberate, methodical approach
    - Prefers familiar patterns and clear feedback
    """
    
    # Limited character familiarity, struggles with symbols
    char_familiarity = {
        'a': 1.1, 'e': 1.1, 'i': 1.1, 'o': 1.1, 'u': 1.1,  # Vowels easier
        't': 1.0, 'h': 1.0, 's': 1.0, 'n': 1.0, 'r': 1.0,  # Common consonants
        '@': 0.6, '#': 0.5, '$': 0.5, '%': 0.4, '^': 0.4, '&': 0.5, '*': 0.5,
        '{': 0.3, '}': 0.3, '[': 0.4, ']': 0.4, '|': 0.3, '\\': 0.3,
        'q': 0.6, 'z': 0.6, 'x': 0.7, 'j': 0.7, 'k': 0.7  # Less familiar letters
    }
    
    common_bigrams = {
        'th': 1.1, 'he': 1.1, 'in': 1.1, 'er': 1.1, 're': 1.1, 'an': 1.1,
        'ed': 1.1, 'ing': 1.1  # Common endings
    }
    
    return UserPersona(
        name="Robert Williams",
        description="Retired teacher learning to use computers more",
        demographics={
            "age": 68,
            "profession": "Retired Teacher",
            "computer_hours_daily": 2,
            "primary_os": "macOS", 
            "computer_experience_years": 5
        },
        experience_level=ExperienceLevel.BEGINNER,
        
        mouse_behavior=MouseBehaviorProfile(
            base_speed=400.0,  # Slow, careful movement
            speed_variance=0.3,  # Variable speed
            acceleration_preference=0.8,  # Gentle acceleration
            precision_level=0.6,  # Less precise
            overshoot_tendency=0.3,  # Often overshoots
            correction_attempts=(2, 5),  # Multiple corrections
            click_duration_ms=(80, 120),  # Longer clicks for confirmation
            double_click_speed_ms=350,  # Slow double clicks
            dwell_time_ms=(150, 400),  # Long pauses before clicking
            curvature_preference=0.6,  # Curved movements
            micro_movements=True,  # Lots of small adjustments
            tremor_intensity=0.8,  # Hand tremor
            scroll_speed=0.6,  # Careful scrolling
            scroll_precision=0.5,  # Imprecise scrolling
            scroll_pause_chance=0.5  # Frequently pauses to read
        ),
        
        keyboard_behavior=KeyboardBehaviorProfile(
            base_wpm=25,  # Slow typing
            wpm_variance=0.4,  # Very variable
            typing_style=TypingStyle.HUNT_AND_PECK,
            inter_key_delay_ms=(200, 500),  # Long delays finding keys
            burst_typing=False,  # Hunt and peck
            burst_length=(2, 4),  # Very short bursts
            burst_pause_ms=(800, 2000),  # Long pauses
            error_rate=0.12,  # Frequent errors
            backspace_usage=0.5,  # Often retypes instead of correcting
            error_correction_delay_ms=(1000, 3000),  # Slow to notice errors
            key_press_duration_ms=(90, 140),  # Long key presses
            key_overlap=False,  # Distinct keystrokes
            modifier_hold_style="sustained",  # Holds modifiers carefully
            character_familiarity=char_familiarity,
            common_bigrams=common_bigrams,
            thinking_pause_chance=0.3,  # Frequent thinking pauses
            thinking_pause_ms=(1000, 3000),  # Long thinking periods
            word_completion_pause_chance=0.2  # Pauses between words
        ),
        
        cognitive_behavior=CognitiveBehaviorProfile(
            decision_speed=0.6,  # Slow, careful decisions
            hesitation_tendency=0.4,  # Often hesitant
            reading_speed_wpm=150,  # Slower reader
            scanning_vs_reading=0.2,  # Prefers careful reading
            attention_span_seconds=(60, 300),  # Shorter attention span
            distraction_probability=0.3,  # Easily distracted
            task_switching_delay_ms=(1000, 2000),  # Slow to switch tasks
            error_detection_delay_ms=(1500, 4000),  # Slow error detection
            patience_level=0.9,  # Very patient
            prefers_keyboard_shortcuts=False,  # Avoids shortcuts
            comfort_with_right_click=0.2,  # Rarely uses right click
            scroll_vs_page_navigation=0.3  # Prefers page navigation
        )
    )


# Persona registry
PERSONAS = {
    "tech_professional": create_tech_professional(),
    "casual_user": create_casual_user(),
    "senior_user": create_senior_user()
}


def get_persona(name: str) -> UserPersona:
    """Get a persona by name"""
    if name not in PERSONAS:
        raise ValueError(f"Unknown persona: {name}. Available: {list(PERSONAS.keys())}")
    return PERSONAS[name]


def list_personas() -> List[str]:
    """Get list of available persona names"""
    return list(PERSONAS.keys())


def get_persona_summary() -> Dict[str, str]:
    """Get summary descriptions of all personas"""
    return {
        name: persona.description 
        for name, persona in PERSONAS.items()
    }
