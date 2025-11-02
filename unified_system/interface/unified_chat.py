from typing import Dict, List, Optional
from datetime import datetime

from ..router.ambiguity_handler import AmbiguityHandler
from ..router.router_agent import IntelligentRouter
from ..manager.system_manager import UnifiedSystemManager
from ..manager.response_formatter import ResponseFormatter

class UnifiedChatSystem:

    def __init__(self, use_agent_router: bool = True):
        
        print("🚀 Initializing Unified Academic Assistant...")
        
        if use_agent_router:
            print("🧠 Using AI-powered Router Agent for natural intent understanding...")
            self.router = IntelligentRouter()
            
        self.ambiguity_handler = AmbiguityHandler() 
        self.system_manager = UnifiedSystemManager()
        self.response_formatter = ResponseFormatter()
        self.use_agent_router = use_agent_router
        

        self.conversation_history = []
        self.current_session = {
            'start_time': datetime.now(),
            'queries_processed': 0,
            'systems_used': set(),
            'errors_encountered': 0
        }
        
        self.user_preferences = {
            'preferred_system': None,
            'response_style': 'detailed',  # 'detailed' or 'brief'
            'show_confidence': True,
            'show_metadata': False
        }
        
        self.awaiting_clarification = False
        self.last_classification_result = None
        
        print("✅ Unified Academic Assistant ready!")
        routing_type = "AI-powered Agent Router" if use_agent_router else "Keyword-based Router"
        print(f"🎯 7 specialized systems available with {routing_type}")
        print("🎯 Systems: Rules UAP | Assistant Search | Rules Mengajar | Correction | Job Query | Material Criteria | Find Room")
    
    def run_interactive(self):
        """
        🔄 Main interactive chat loop
        """
        
        welcome = self.response_formatter.format_welcome_message()
        print(f"\n{welcome}")
        
        while True:
            try:
                user_input = input("\n💬 Tanya apa aja: ").strip()
                
                # Handle exit commands
                if self._check_exit_commands(user_input):
                    break
                
                # Handle empty input
                if not user_input:
                    print("❓ Silakan masukkan pertanyaan atau ketik 'help' untuk bantuan")
                    continue
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    continue
                
                # Process the query
                response = self.process_unified_query(user_input)
                
                # Display response
                print(f"\n{response}")
                
                # Update session stats
                self._update_session_stats()
                
            except KeyboardInterrupt:
                print("\n\n👋 Sampai jumpa! Terima kasih sudah menggunakan Unified Academic Assistant")
                break
            except Exception as e:
                print(f"\n💥 System error: {str(e)}")
                print("💡 Silakan coba lagi atau ketik 'help' untuk bantuan")
                self.current_session['errors_encountered'] += 1
    
    def process_unified_query(self, query: str) -> str:

        try:
            print(f"🔄 Processing: '{query}'")
            
            if self.awaiting_clarification and self.last_classification_result:
                return self._handle_clarification_response(query)
            
            classification_result = self.router.classify_intent(query)
            
            if classification_result['system'] == 'ambiguous':
                return self._handle_ambiguous_classification(classification_result, query)
            elif classification_result['classification_type'] == 'low_confidence':
                return self._handle_low_confidence_classification(classification_result, query)
            else:
                return self._execute_system_query(classification_result, query)
            
        except Exception as e:
            error_msg = f"💥 Error processing query: {str(e)}"
            print(error_msg)
            return self.response_formatter.format_error_response(
                str(e), 'unified_system', query
            )
    
    def _handle_ambiguous_classification(self, classification_result: Dict, query: str) -> str:
        """Handle completely ambiguous queries"""
        
        self.awaiting_clarification = True
        self.last_classification_result = classification_result
        
        ambiguity_response = self.ambiguity_handler.handle_ambiguous_query(
            classification_result, query
        )
        
        return ambiguity_response
    
    def _handle_low_confidence_classification(self, classification_result: Dict, query: str) -> str:
        
        confidence = classification_result.get('confidence', 0.0)
        
        if confidence < 0.3:
            return self._handle_ambiguous_classification(classification_result, query)
        
        warning_response = self.ambiguity_handler.handle_ambiguous_query(
            classification_result, query
        )
        
        system_response = self._execute_system_query(classification_result, query)
        
        return f"{warning_response}\n\n---\n\n{system_response}"
    
    def _handle_clarification_response(self, user_input: str) -> str:
        """Handle user responses to clarification questions"""
        
        selected_system = self.ambiguity_handler.parse_user_selection(user_input)
        
        if selected_system:
            self.awaiting_clarification = False
            
            classification_result = {
                'system': selected_system,
                'confidence': 1.0,  # User explicitly selected
                'classification_type': 'user_selected',
                'query': self.last_classification_result.get('query', user_input)
            }
            
            original_query = self.last_classification_result.get('query', user_input)
            self.last_classification_result = None
            
            # Execute with selected system
            return self._execute_system_query(classification_result, original_query)
        
        else:
            # User didn't select a valid option, treat as new query
            self.awaiting_clarification = False
            self.last_classification_result = None
            
            # Process as new query
            return self.process_unified_query(user_input)
    
    def _execute_system_query(self, classification_result: Dict, query: str) -> str:
        """Execute query on the appropriate system"""
        
        system_type = classification_result['system']
        
        # Track system usage
        self.current_session['systems_used'].add(system_type)
        
        # Execute query through system manager
        response = self.system_manager.route_and_execute(classification_result, query)
        
        # Store in conversation history
        self._add_to_history(query, response, classification_result)
        
        return response
    
    def _check_exit_commands(self, user_input: str) -> bool:
        """Check if user wants to exit"""
        
        exit_commands = ['exit', 'quit', 'bye', 'keluar', 'selesai', 'q']
        
        if user_input.lower() in exit_commands:
            # Show session summary
            self._show_session_summary()
            print("\n👋 Terima kasih sudah menggunakan Unified Academic Assistant!")
            print("🎓 Semoga membantu kebutuhan akademik kamu!")
            return True
        
        return False
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like help, info, etc."""
        
        command = user_input.lower().strip()
        
        if command == 'help':
            help_response = self.response_formatter.format_help_response('general')
            print(f"\n{help_response}")
            return True
        
        elif command == 'systems':
            systems_response = self.response_formatter.format_help_response('systems')
            print(f"\n{systems_response}")
            return True
        
        elif command == 'tips':
            tips_response = self.response_formatter.format_help_response('tips')
            print(f"\n{tips_response}")
            return True
        
        elif command == 'status':
            self._show_system_status()
            return True
        
        elif command == 'history':
            self._show_conversation_history()
            return True
        
        elif command == 'clear':
            self._clear_conversation_history()
            return True
        
        elif command in ['1', '2', '3', '4']:
            # Direct system selection
            system_map = {
                '1': 'rules_uap',
                '2': 'assistant_search',
                '3': 'rules_mengajar', 
                '4': 'correction_casemaking'
            }
            selected_system = system_map[command]
            print(f"🎯 Sistem {selected_system} dipilih. Silakan tanya sesuatu!")
            self.user_preferences['preferred_system'] = selected_system
            return True
        
        return False
    
    def _show_system_status(self):
        """Show current system status"""
        
        status = self.system_manager.get_system_status()
        
        print("\n📊 **SYSTEM STATUS**")
        print("=" * 30)
        print(f"🟢 Loaded systems: {len(status['loaded_systems'])}")
        for system in status['loaded_systems']:
            print(f"   • {system}")
        
        print(f"\n🟡 Available systems: {len(status['available_systems'])}")
        for system in status['available_systems']:
            if system not in status['loaded_systems']:
                print(f"   • {system} (not loaded)")
        
        print(f"\n📈 Session stats:")
        print(f"   • Queries processed: {self.current_session['queries_processed']}")
        print(f"   • Systems used: {len(self.current_session['systems_used'])}")
        print(f"   • Errors: {self.current_session['errors_encountered']}")
    
    def _show_conversation_history(self):
        """Show recent conversation history"""
        
        if not self.conversation_history:
            print("\n📝 **CONVERSATION HISTORY**")
            print("Belum ada riwayat percakapan.")
            return
        
        print("\n📝 **CONVERSATION HISTORY** (10 terakhir)")
        print("=" * 50)
        
        recent_history = self.conversation_history[-10:]
        
        for i, entry in enumerate(recent_history, 1):
            timestamp = entry['timestamp'].strftime("%H:%M:%S")
            query = entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query']
            system = entry['classification']['system']
            
            print(f"{i}. [{timestamp}] {system}")
            print(f"   Q: {query}")
            print()
    
    def _clear_conversation_history(self):
        """Clear conversation history"""
        
        self.conversation_history.clear()
        print("\n🗑️ Riwayat percakapan telah dihapus.")
    
    def _show_session_summary(self):
        """Show session summary before exit"""
        
        duration = datetime.now() - self.current_session['start_time']
        minutes = int(duration.total_seconds() / 60)
        
        print("\n📊 **SESSION SUMMARY**")
        print("=" * 30)
        print(f"⏱️ Duration: {minutes} menit")
        print(f"💬 Queries processed: {self.current_session['queries_processed']}")
        print(f"🎯 Systems used: {len(self.current_session['systems_used'])}")
        if self.current_session['systems_used']:
            for system in self.current_session['systems_used']:
                print(f"   • {system}")
        print(f"❌ Errors: {self.current_session['errors_encountered']}")
    
    def _add_to_history(self, query: str, response: str, classification: Dict):
        """Add interaction to conversation history"""
        
        entry = {
            'timestamp': datetime.now(),
            'query': query,
            'response': response,
            'classification': classification
        }
        
        self.conversation_history.append(entry)
        
        # Keep only last 50 entries
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def _update_session_stats(self):
        """Update session statistics"""
        
        self.current_session['queries_processed'] += 1
    
    def process_direct_query(self, query: str) -> str:
        """
        Process a single query (for direct/non-interactive use)
        Enhanced to handle ambiguous queries by choosing best match
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        
        try:
            print(f"🔄 Processing: '{query}'")
            
            # Stage 1: Intent Classification
            classification_result = self.router.classify_intent(query)
            
            # Stage 2: Enhanced Direct Mode Logic
            if classification_result['system'] == 'ambiguous':
                return self._handle_ambiguous_direct_query(classification_result, query)
            elif classification_result['classification_type'] == 'low_confidence':
                return self._handle_low_confidence_direct_query(classification_result, query)
            else:
                return self._execute_system_query(classification_result, query)
            
        except Exception as e:
            error_msg = f"💥 Error processing query: {str(e)}"
            print(error_msg)
            return self.response_formatter.format_error_response(
                str(e), 'unified_system', query
            )
    
    def _handle_ambiguous_direct_query(self, classification_result: Dict, query: str) -> str:
        """
        Handle ambiguous queries in direct mode by choosing the best match
        """
        
        # Get the highest scoring system from classification
        scores = classification_result.get('all_scores', {})
        
        if scores:
            # Choose system with highest score
            best_system = max(scores.items(), key=lambda x: x[1])
            system_name = best_system[0]
            confidence = best_system[1]
            
            # Create new classification result with best guess
            new_classification = {
                'system': system_name,
                'confidence': confidence,
                'classification_type': 'best_guess_direct_mode',
                'original_classification': 'ambiguous'
            }
            
            print(f"🎯 Direct mode: Using best guess → {system_name} (confidence: {confidence:.1%})")
            
            # Execute with best guess
            response = self._execute_system_query(new_classification, query)
            
            # Add disclaimer
            disclaimer = f"\n\n💡 **Note:** Query was ambiguous, executed with best guess ({system_name}). For interactive clarification, use: `python run_unified_chat.py` (no arguments)"
            
            return response + disclaimer
        
        else:
            # Final fallback
            return "❓ Query terlalu ambiguous untuk direct mode. Gunakan interactive mode: `python run_unified_chat.py`"
    
    def _handle_low_confidence_direct_query(self, classification_result: Dict, query: str) -> str:
        """
        Handle low confidence queries in direct mode
        """
        
        confidence = classification_result.get('confidence', 0.0)
        
        # If confidence is very low (< 0.3), treat as ambiguous
        if confidence < 0.3:
            return self._handle_ambiguous_direct_query(classification_result, query)
        
        # Otherwise, proceed with warning but execute
        print(f"⚠️ Direct mode: Low confidence ({confidence:.1%}), executing anyway...")
        
        response = self._execute_system_query(classification_result, query)
        
        # Add warning
        warning = f"\n\n⚠️ **Warning:** Classification confidence was low ({confidence:.1%}). Result may not be accurate."
        
        return response + warning

if __name__ == "__main__":
    # Test the unified chat system
    print("🧪 Testing Unified Chat System")
    print("=" * 40)
    
    # Initialize system
    chat_system = UnifiedChatSystem()
    
    # Test direct query processing
    test_queries = [
        "Bagaimana aturan menyontek?",
        "Siapa asisten di Syahdan?", 
        "template"  # Ambiguous
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        response = chat_system.process_direct_query(query)
        print(f"Response: {response[:100]}...")
        print("-" * 40) 