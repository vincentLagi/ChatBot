"""
Unified Academic Assistant System
Single interface for all academic assistance needs

Components:
- Router: Intent classification and query routing
- Manager: System loading and execution management  
- Interface: Unified chat interface

Systems integrated:
- Rules UAP System
- Assistant Search System
- Practicum Rules System  
- Correction & Case Making System
"""

from .router import SmartIntentRouter, AmbiguityHandler, IntelligentRouter
from .manager import UnifiedSystemManager, ResponseFormatter
from .interface import UnifiedChatSystem

__version__ = "1.0.0"
__author__ = "Academic Assistant Team"
__description__ = "Unified Academic Assistant with intelligent AI-powered query routing"

# Package-level exports
__all__ = [
    'SmartIntentRouter',
    'IntelligentRouter',
    'AmbiguityHandler', 
    'UnifiedSystemManager',
    'ResponseFormatter',
    'UnifiedChatSystem'
] 