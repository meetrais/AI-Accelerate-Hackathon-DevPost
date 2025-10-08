"""
Enhanced Flask Application v2.0 with MCP, A2A, and AP2
"""
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import asyncio
import uuid
import os
from dotenv import load_dotenv

# v1.0 imports
from modules.elasticsearch_setup import get_elasticsearch_client
from modules.search import search_travel_data
from modules.agent import chat_stream, extract_preferences, generate_itinerary
from modules.data_loader import initialize_vertex_ai

# v2.0 imports
from agents.flight_agent import flight_agent
from agents.payment_agent import payment_agent
from agents.orchestrator import orchestrator
from shared.database import init_database, get_session, Booking, Payment, User
from shared.redis_client import redis_client

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
try:
    initialize_vertex_ai()
    es_client = get_elasticsearch_client()
    init_database()
    print("✓ All services initialized successfully")
except Exception as e:
    print(f"✗ Error initializing services: {e}")
    es_client = None

# Store conversation state
conversations = {}

# ============================================================================
# v1.0 Endpoints (Keep existing functionality)
# ============================================================================

@app.route('/')
def index():
    """Serve main page - v2.0 enhanced UI"""
    return render_template('index_v2.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'elasticsearch': es_client is not None and es_client.ping(),
        'redis': redis_client.ping(),
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
        
        # Extract preferences
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

# ============================================================================
# v2.0 Enhanced Endpoints (New functionality)
# ============================================================================

@app.route('/api/v2/flights/search', methods=['POST'])
async def search_flights_v2():
    """Search flights using Flight Agent"""
    try:
        data = request.json
        
        # Send request to flight agent via orchestrator
        result = await orchestrator.send_message(
            to_agent="flight_agent",
            action="search_flights",
            parameters={
                "origin": data.get("origin"),
                "destination": data.get("destination"),
                "date": data.get("date"),
                "passengers": data.get("passengers", 1)
            }
        )
        
        # In production, wait for async response
        # For demo, call directly
        flights_result = await flight_agent.search_flights(
            parameters={
                "origin": data.get("origin"),
                "destination": data.get("destination"),
                "date": data.get("date"),
                "passengers": data.get("passengers", 1)
            }
        )
        
        return jsonify(flights_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/booking/complete-trip', methods=['POST'])
async def book_complete_trip():
    """Book complete trip using orchestrator"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['origin', 'destination', 'departure_date', 'passengers', 
                   'passenger_details', 'payment_method', 'total_amount']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Execute workflow via orchestrator
        result = await orchestrator.book_complete_trip(
            parameters=data
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/payment/process', methods=['POST'])
async def process_payment():
    """Process payment using Payment Agent with AP2 protocol"""
    try:
        data = request.json
        
        # Validate payment data
        required = ['amount', 'payment_method']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process payment via payment agent
        result = await payment_agent.process_payment(
            parameters={
                "amount": data["amount"],
                "currency": data.get("currency", "USD"),
                "payment_method": data["payment_method"],
                "metadata": data.get("metadata", {})
            }
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/bookings', methods=['GET'])
def get_user_bookings():
    """Get all bookings for a user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        session = get_session()
        try:
            bookings = session.query(Booking).filter_by(user_id=user_id).all()
            
            result = []
            for booking in bookings:
                result.append({
                    'id': booking.id,
                    'type': booking.type,
                    'status': booking.status,
                    'details': booking.details,
                    'amount': booking.amount,
                    'currency': booking.currency,
                    'confirmation_number': booking.confirmation_number,
                    'created_at': booking.created_at.isoformat() if booking.created_at else None
                })
            
            return jsonify({'bookings': result})
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/agents/status', methods=['GET'])
def get_agents_status():
    """Get status of all agents"""
    return jsonify({
        'orchestrator': orchestrator.get_status(),
        'flight_agent': flight_agent.get_status(),
        'payment_agent': payment_agent.get_status()
    })

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
