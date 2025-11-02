
"""
Unified System Manager for Academic Assistant
Manages loading, routing, and execution of specialized systems

Features:
- Lazy loading of systems (performance optimization)
- System caching and reuse
- Execution routing and coordination
- Error handling and fallbacks
"""

from typing import Dict, Optional, Any
from datetime import datetime
import time

class UnifiedSystemManager:
    """
    🎛️ Central manager for all specialized academic assistance systems
    
    Responsibilities:
    - Load systems on-demand (lazy loading)
    - Cache initialized systems for reuse
    - Route queries to appropriate systems
    - Handle system errors and fallbacks
    """
    
    def __init__(self):
        """Initialize the system manager"""
        
        # System cache - loaded systems are stored here
        self._systems = {}
        
        self._loading_status = {}
        
        self._system_loaders = {
            'general_response': self._load_general_response_system,
            'rules_uap': self._load_rules_uap_system,
            'assistant_search': self._load_assistant_search_system,
            'rules_mengajar': self._load_rules_mengajar_system,
            'correction_casemaking': self._load_correction_casemaking_system,
            'job_query': self._load_job_query_system,
            'material_criteria': self._load_material_criteria_system,
            'find_room': self._load_find_room_system
        }
        
        # System metadata
        self._system_info = {
            'rules_uap': {
                'name': 'Rules UAP System',
                'description': 'Academic rules and violations system'
            },
            'assistant_search': {
                'name': 'Assistant Search System',
                'description': 'Teaching assistant and staff search system'
            },
            'rules_mengajar': {
                'name': 'Rules Mengajar System',
                'description': 'Laboratory and teaching procedures system'
            },
            'correction_casemaking': {
                'name': 'Correction & Case Making System',
                'description': 'Grading and exam creation system'
            },
            'job_query': {
                'name': 'Job Query System',
                'description': 'Assistant job schedule and availability system'
            },
            'material_criteria': {
                'name': 'Material and Criteria System',
                'description': 'Course materials and criteria search system'
            },
            'find_room': {
                'name': 'Find Room System',
                'description': 'Room availability and schedule search system'
            }
        }
        
        print("🎛️ Unified System Manager initialized successfully!")
    
    def route_and_execute(self, classification_result: Dict, query: str) -> str:
        """
        🚀 Main execution method - route and execute query
        
        Args:
            classification_result: Result from intent classifier
            query: User query string
            
        Returns:
            Response from the appropriate system
        """
        
        system_type = classification_result.get('system')
        confidence = classification_result.get('confidence', 0.0)
        classification_type = classification_result.get('classification_type', 'unknown')
        
        print(f"🎯 Routing to system: {system_type} (confidence: {confidence:.3f})")
        
        if system_type not in self._system_loaders:
            return f"❌ Error: Unknown system '{system_type}'. Available systems: {list(self._system_loaders.keys())}"
        
        try:
            system = self._get_or_load_system(system_type)
            if system is None:
                return f"❌ Error: Failed to load {system_type} system. Please try again."
            
            print(f"🤖 Executing query on {system_type} system...")
            response = system.process_query(query)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error executing query on {system_type} system: {str(e)}"
            print(error_msg)
            return self._generate_error_fallback(system_type, query, str(e))
    
    def _get_or_load_system(self, system_type: str):
        """
        ⚡ Get system from cache or load it (lazy loading)
        """
        
        # Return cached system if available
        if system_type in self._systems:
            print(f"♻️ Using cached {system_type} system")
            return self._systems[system_type]
        
        # Check if currently loading (prevent duplicate loads)
        if self._loading_status.get(system_type, False):
            print(f"⏳ {system_type} system is currently loading...")
            return None
        
        # Load the system
        print(f"🔧 Loading {system_type} system for first time...")
        self._loading_status[system_type] = True
        
        try:
            loader_func = self._system_loaders[system_type]
            system = loader_func()
            
            if system is not None:
                # Cache the loaded system
                self._systems[system_type] = system
                print(f"✅ {system_type} system loaded and cached successfully!")
                return system
            else:
                print(f"❌ Failed to load {system_type} system")
                return None
                
        except Exception as e:
            print(f"💥 Error loading {system_type} system: {str(e)}")
            return None
            
        finally:
            self._loading_status[system_type] = False
    
    def _load_general_response_system(self):
        """Load General Response system"""
        
        try:
            from ..router.router_agent import IntelligentRouter
            
            class GeneralResponseSystem:
                def __init__(self):
                    self.router = IntelligentRouter()
                
                def process_query(self, query: str) -> str:
                    """Generate general response for greetings and basic info"""
                    return self.router.generate_general_response(query)
            
            print("✅ General Response system loaded successfully")
            return GeneralResponseSystem()
            
        except Exception as e:
            print(f"❌ Error loading General Response system: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_rules_uap_system(self):
        """Load Rules UAP system"""
        
        try:
            from systems.rules_uap.agents import create_rules_uap_agents
            from systems.rules_uap.tasks import  create_rules_answer_task as create_rules_uap_answer_task
            from crewai import Crew
            
            class RulesUAPSystem:
                def __init__(self):
                    answer_agent = create_rules_uap_agents()
                    self.answer_agent = answer_agent
                
                def process_query(self, query: str) -> str:
                    print(f"🔍 Rules UAP: Processing query '{query}'")
                    
                    answer_task = create_rules_uap_answer_task(
                        agent=self.answer_agent,
                        user_query=query,
                        context=[],
                    )
                    
                    crew = Crew(
                        agents=[self.answer_agent],
                        tasks=[answer_task],
                        process='sequential',
                        verbose=True,  # Enable verbose for debugging
                        max_iter=3,
                        memory=False  # Disable memory to avoid conflicts
                    )
                    
                    print(f"🚀 Rules UAP: Starting crew execution...")
                    result = crew.kickoff()
                    print(f"✅ Rules UAP: Crew execution completed")
                    
                    return str(result)
            
            return RulesUAPSystem()
            
        except Exception as e:
            print(f"❌ Error loading Rules UAP system: {e}")
            return None
    
    def _load_assistant_search_system(self):
        """Load Assistant Search system"""
        
        try:
            from systems.assistant_search.agents import create_assistant_agents
            from systems.assistant_search.tasks import create_assistant_search_workflow_tasks
            from crewai import Crew
            
            class AssistantSearchSystem:
                def __init__(self):
                    query_agent, answer_agent = create_assistant_agents()
                    self.query_agent = query_agent
                    self.answer_agent = answer_agent
                
                def process_query(self, query: str) -> str:
                    print(f"🔍 Assistant Search: Processing query '{query}'")
                    
                    tasks = create_assistant_search_workflow_tasks(
                        self.query_agent, 
                        self.answer_agent, 
                        query
                    )
                    
                    crew = Crew(
                        agents=[self.query_agent, self.answer_agent],
                        tasks=tasks,
                        process='sequential',
                        verbose=True
                    )
                    
                    max_retries = 3
                    last_exception = None
                    for attempt in range(max_retries):
                        try:
                            result = crew.kickoff()
                            return str(result)
                        except Exception as e:
                            last_exception = e
                            if "503" in str(e) and attempt < max_retries - 1:
                                print(f"🔥 LLM model overloaded (503). Retrying in 3 seconds... (Attempt {attempt + 1}/{max_retries})")
                                time.sleep(3)
                                continue
                            else:
                                break
                    raise last_exception
            
            return AssistantSearchSystem()
            
        except Exception as e:
            print(f"❌ Error loading Assistant Search system: {e}")
            return None
    
    def _load_rules_mengajar_system(self):
        """Load Rules Mengajar system"""
        
        try:
            from systems.rules_mengajar.agents import get_practicum_agents
            from systems.rules_mengajar.tasks import create_practicum_answer_task
            from crewai import Crew
            
            class RulesMengajarSystem:
                def __init__(self):
                    agents = get_practicum_agents()
                    self.answer_agent = agents['answer_agent']
                
                def process_query(self, query: str) -> str:
                    answer_task = create_practicum_answer_task(
                        agent=self.answer_agent,
                        search_results_context=[],
                        user_query=query,
                        context=[]
                    )
                    
                    crew = Crew(
                        agents=[ self.answer_agent],
                        tasks=[answer_task],
                        process='sequential',
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    return str(result)
            
            return RulesMengajarSystem()
            
        except Exception as e:
            print(f"❌ Error loading Rules Mengajar system: {e}")
            return None
    
    def _load_correction_casemaking_system(self):
        """Load Correction & Case Making system"""
        
        try:
            from systems.correction_casemaking.agents import create_correction_query_agent, create_correction_answer_agent
            from systems.correction_casemaking.tasks import create_correction_search_task, create_correction_answer_task
            from crewai import Crew
            
            class CorrectionCaseMakingSystem:
                def __init__(self):
                    self.query_agent, self.answer_agent = create_correction_query_agent(), create_correction_answer_agent()
                
                def process_query(self, query: str) -> str:
                    search_task = create_correction_search_task(self.query_agent, query)
                    answer_task = create_correction_answer_task(
                        agent=self.answer_agent,
                        search_results_context=[search_task],
                        user_query=query,
                        context=[search_task]
                    )
                    
                    crew = Crew(
                        agents=[self.query_agent, self.answer_agent],
                        tasks=[search_task, answer_task],
                        process='sequential',
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    return str(result)
            
            return CorrectionCaseMakingSystem()
            
        except Exception as e:
            print(f"❌ Error loading Correction & Case Making system: {e}")
            return None
    
    def _load_job_query_system(self):
        """Load Job Query system"""
        
        try:
            from systems.job_query.agents import create_job_agents
            from systems.job_query.tasks import create_job_workflow_tasks
            from crewai import Crew
            
            class JobQuerySystem:
                def __init__(self):
                    query_agent, answer_agent = create_job_agents()
                    self.query_agent = query_agent
                    self.answer_agent = answer_agent
                
                def process_query(self, query: str) -> str:
                    tasks = create_job_workflow_tasks(
                        self.query_agent, 
                        self.answer_agent, 
                        query
                    )
                    
                    crew = Crew(
                        agents=[self.query_agent, self.answer_agent],
                        tasks=tasks,
                        process='sequential',
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    return str(result)
            
            return JobQuerySystem()
            
        except Exception as e:
            print(f"❌ Error loading Job Query system: {e}")
            return None
    
    def _load_material_criteria_system(self):
        """Load Material and Criteria system"""
        
        try:
            from systems.material_criteria.agents import create_material_criteria_agents
            from systems.material_criteria.tasks import create_material_criteria_workflow_tasks
            from crewai import Crew
            
            # Create system wrapper
            class MaterialCriteriaSystem:
                def __init__(self):
                    agents = create_material_criteria_agents()
                    self.search_agent = agents['material_search_agent']
                    self.info_agent = agents['material_info_agent']
                
                def process_query(self, query: str) -> str:
                    tasks = create_material_criteria_workflow_tasks(
                        self.search_agent,
                        self.info_agent, 
                        query
                    )
                    
                    crew = Crew(
                        agents=[self.search_agent, self.info_agent],
                        tasks=tasks,
                        process='sequential',
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    return str(result)
            
            return MaterialCriteriaSystem()
            
        except Exception as e:
            print(f"❌ Error loading Material and Criteria system: {e}")
            return None
    
    def _load_find_room_system(self):
        """Load Find Room system"""
        
        try:
            from systems.find_room.agents import create_room_agents
            from systems.find_room.tasks import create_room_workflow_tasks
            from crewai import Crew
            
            # Create system wrapper
            class FindRoomSystem:
                def __init__(self):
                    query_agent, answer_agent = create_room_agents()
                    self.query_agent = query_agent
                    self.answer_agent = answer_agent
                
                def process_query(self, query: str) -> str:
                    tasks = create_room_workflow_tasks(
                        self.query_agent,
                        self.answer_agent,
                        query
                    )
                    
                    crew = Crew(
                        agents=[self.query_agent, self.answer_agent],
                        tasks=tasks,
                        process='sequential',
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    return str(result)
            
            return FindRoomSystem()
            
        except Exception as e:
            print(f"❌ Error loading Find Room system: {e}")
            return None
    
    
    def get_system_status(self) -> Dict:
        """
        📊 Get status of all systems
        """
        
        status = {
            'loaded_systems': list(self._systems.keys()),
            'loading_systems': [k for k, v in self._loading_status.items() if v],
            'available_systems': list(self._system_loaders.keys()),
            'system_info': self._system_info
        }
        
        return status
    
    def preload_system(self, system_type: str) -> bool:
        """
        🔧 Preload a specific system (useful for warming up)
        """
        
        if system_type not in self._system_loaders:
            print(f"❌ Unknown system: {system_type}")
            return False
        
        system = self._get_or_load_system(system_type)
        return system is not None
    
    def clear_system_cache(self, system_type: Optional[str] = None):
        """
        🗑️ Clear system cache (for memory management)
        """
        
        if system_type:
            if system_type in self._systems:
                del self._systems[system_type]
                print(f"🗑️ Cleared {system_type} from cache")
        else:
            self._systems.clear()
            print("🗑️ Cleared all systems from cache")
