from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import uuid
import os
from dotenv import load_dotenv

from modules.elasticsearch_setup import get_elasticsearch_client
from modules.search import search_travel_data
from modules.agent import chat, chat_stream, extract_preferences, generate_itinerary
from modules.data_loader import initialize_vertex_ai

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
try:
    initialize_vertex_ai()
    es_client = get_elasticsearch_client()
    print("✓ Services initialized successfully")
except Exception as e:
    print(f"✗ Error initializing services: {e}")
    es_client = None

# Store conversation state (in production, use Redis or database)
conversations = {}

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'elasticsearch': es_client is not None and es_client.ping(),
        'vertex_ai': os.getenv('GOOGLE_CLOUD_PROJECT') is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat messages with streaming response"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not es_client:
            return jsonify({'error': 'Search service unavailable'}), 503
        
        # Get or create conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                'messages': [],
                'preferences': {}
            }
        
        conversation = conversations[conversation_id]
        
        # Extract preferences from message
        new_prefs = extract_preferences(user_message, conversation['messages'])
        conversation['preferences'].update(new_prefs)
        
        # Search for relevant travel data
        search_results = search_travel_data(es_client, user_message, size=10)
        
        # Generate streaming response
        def generate():
            full_response = ""
            for chunk in chat_stream(user_message, search_results, 
                                    conversation['messages'], 
                                    conversation['preferences']):
                full_response += chunk
                yield chunk
            
            # Save conversation
            conversation['messages'].append({'role': 'user', 'content': user_message})
            conversation['messages'].append({'role': 'assistant', 'content': full_response})
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/itinerary', methods=['POST'])
def itinerary_endpoint():
    """Generate complete itinerary"""
    try:
        data = request.json
        destination = data.get('destination', '')
        days = data.get('days', 3)
        preferences = data.get('preferences', {})
        
        if not destination:
            return jsonify({'error': 'Destination is required'}), 400
        
        if not es_client:
            return jsonify({'error': 'Search service unavailable'}), 503
        
        # Generate itinerary
        itinerary = generate_itinerary(destination, days, preferences, es_client)
        
        return jsonify({
            'destination': destination,
            'days': days,
            'itinerary': itinerary
        })
        
    except Exception as e:
        print(f"Error in itinerary endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)

