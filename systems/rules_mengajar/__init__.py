"""
Practicum Rules System
Handles queries about practicum procedures, lab rules, and computer setup

System Components:
- agents.py: Query processing and answer generation agents
- tasks.py: Task definitions for agent workflows  
- tools.py: Search tools for practicum database
"""

from .agents import create_practicum_answer_agent
from .tasks import create_practicum_answer_task

# Backward compatibility
def create_practicum_agents():
    """Create both practicum agents for the workflow"""
    answer_agent = create_practicum_answer_agent()
    return answer_agent

__all__ = [
    'create_practicum_answer_agent', 
    'create_practicum_answer_task',
    'create_practicum_agents'
] 