"""
BrowserGeist Python SDK

Human-like browser automation framework for macOS.
"""

from .browsergeist import (
    HumanMouse, 
    AsyncHumanMouse,
    MotionProfiles, 
    MotionProfile,
    target,
    automation_session,
    BrowserGeistError,
    ConnectionError,
    CommandError,
    VisionError,
    CommandResult
)

from .captcha_solver import (
    CaptchaSolver,
    CaptchaSolveMethod, 
    CaptchaSolution
)

from .user_personas import (
    UserPersona,
    get_persona,
    list_personas,
    PERSONAS
)

__version__ = "1.0.0"
__author__ = "BrowserGeist Team"

__all__ = [
    'HumanMouse',
    'AsyncHumanMouse', 
    'MotionProfiles',
    'MotionProfile',
    'target',
    'automation_session',
    'BrowserGeistError',
    'ConnectionError', 
    'CommandError',
    'VisionError',
    'CommandResult',
    'CaptchaSolver',
    'CaptchaSolveMethod',
    'CaptchaSolution',
    'UserPersona',
    'get_persona',
    'list_personas',
    'PERSONAS'
]
