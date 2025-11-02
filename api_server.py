#!/usr/bin/env python3
"""
Flask API Server for AI Agent
Provides REST API endpoints for the Line Bot to interact with the AI Agent system
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the unified chat system
from unified_system.interface.unified_chat import UnifiedChatSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store the chat system instance
chat_system = None

def initialize_chat_system():
    """Initialize the unified chat system"""
    global chat_system
    try:
        logger.info("🚀 Initializing Unified Chat System...")
        chat_system = UnifiedChatSystem(use_agent_router=True)
        logger.info("✅ Chat system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize chat system: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Agent API',
        'chat_system_ready': chat_system is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint for processing user messages
    
    Expected JSON payload:
    {
        "message": "user message here",
        "session_id": "optional session identifier"
    }
    
    Returns:
    {
        "status": "success" | "error",
        "message": "response message",
        "timestamp": "ISO timestamp",
        "session_id": "session identifier"
    }
    """
    
    try:
        # Check if chat system is initialized
        if chat_system is None:
            return jsonify({
                'status': 'error',
                'message': 'Chat system not initialized. Please try again.',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Extract message and session_id
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({
                'status': 'error',
                'message': 'No message provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Log the incoming request
        logger.info(f"📨 Received message from session {session_id}: {user_message[:100]}...")
        
        # Process the message using the unified chat system
        response = chat_system.process_direct_query(user_message)
        
        # Log the response
        logger.info(f"📤 Sending response to session {session_id}: {response[:100]}...")
        
        # Return the response
        return jsonify({
            'status': 'success',
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/systems', methods=['GET'])
def get_systems_info():
    """Get information about available AI systems"""
    try:
        systems_info = {
            'available_systems': [
                'Rules UAP',
                'Assistant Search', 
                'Rules Mengajar',
                'Correction',
                'Job Query',
                'Material Criteria',
                'Find Room'
            ],
            'description': 'Unified Academic Assistant with 7 specialized AI systems',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(systems_info)
        
    except Exception as e:
        logger.error(f"❌ Error getting systems info: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting systems info: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get detailed system status"""
    try:
        status = {
            'chat_system_ready': chat_system is not None,
            'service': 'AI Agent API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        
        if chat_system:
            status['session_info'] = {
                'start_time': chat_system.current_session['start_time'].isoformat(),
                'queries_processed': chat_system.current_session['queries_processed'],
                'systems_used': list(chat_system.current_session['systems_used']),
                'errors_encountered': chat_system.current_session['errors_encountered']
            }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Error getting status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

def main():
    """Main function to run the Flask server"""
    
    # Initialize the chat system
    if not initialize_chat_system():
        logger.error("❌ Failed to initialize chat system. Exiting...")
        return
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    logger.info(f"🚀 Starting AI Agent API server on port {port}")
    logger.info("📡 Available endpoints:")
    logger.info("   - POST /api/chat - Main chat endpoint")
    logger.info("   - GET  /health - Health check")
    logger.info("   - GET  /api/systems - Get systems info")
    logger.info("   - GET  /api/status - Get detailed status")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # Set to False for production
        threaded=True
    )

if __name__ == '__main__':
    main() 