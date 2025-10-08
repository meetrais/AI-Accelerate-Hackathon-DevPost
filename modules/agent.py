import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

SYSTEM_PROMPT = """You are an enthusiastic and knowledgeable travel planning assistant. Your goal is to help users plan amazing trips by providing personalized recommendations based on their preferences and interests.

Key guidelines:
- Be conversational, friendly, and helpful
- Ask clarifying questions when user preferences are unclear (budget, travel dates, interests, group size)
- Use the provided travel data to make specific recommendations with names, locations, and details
- Explain WHY you're recommending something based on user preferences
- Include practical information like price ranges, ratings, and best times to visit
- If you don't have information in the search results, be honest and suggest alternatives
- Format responses clearly with recommendations organized by type (destinations, activities, hotels, restaurants)
"""

def extract_preferences(message, conversation_history=None):
    """Extract user preferences from conversation"""
    preferences = {}
    
    message_lower = message.lower()
    
    # Budget detection
    if any(word in message_lower for word in ['cheap', 'budget', 'affordable', 'inexpensive']):
        preferences['budget'] = 'low'
        preferences['price_range'] = '$'
    elif any(word in message_lower for word in ['luxury', 'expensive', 'high-end', 'upscale']):
        preferences['budget'] = 'high'
        preferences['price_range'] = '$$$'
    elif any(word in message_lower for word in ['moderate', 'mid-range', 'reasonable']):
        preferences['budget'] = 'moderate'
        preferences['price_range'] = '$$'
    
    # Interest detection
    interests = []
    interest_keywords = {
        'cultural': ['culture', 'cultural', 'temple', 'museum', 'history', 'historical'],
        'nature': ['nature', 'hiking', 'mountain', 'beach', 'outdoor', 'scenic'],
        'food': ['food', 'restaurant', 'cuisine', 'dining', 'eat'],
        'adventure': ['adventure', 'exciting', 'thrill', 'active'],
        'relaxation': ['relax', 'spa', 'peaceful', 'calm', 'quiet'],
        'romantic': ['romantic', 'honeymoon', 'couple'],
        'photography': ['photo', 'photography', 'instagram']
    }
    
    for interest, keywords in interest_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            interests.append(interest)
    
    if interests:
        preferences['interests'] = interests
    
    return preferences

def build_rag_prompt(user_message, search_results, conversation_history=None, preferences=None):
    """Build RAG prompt with search results as context"""
    
    # Format search results
    context = "AVAILABLE TRAVEL OPTIONS:\n\n"
    
    for i, result in enumerate(search_results, 1):
        context += f"{i}. {result['name']} ({result['type'].upper()})\n"
        context += f"   Location: {result['location'].get('city', '')}, {result['location'].get('country', '')}\n"
        context += f"   Description: {result['description']}\n"
        context += f"   Price: {result.get('price_range', 'N/A')} | Rating: {result.get('rating', 'N/A')}/5\n"
        
        if result.get('categories'):
            context += f"   Categories: {', '.join(result['categories'])}\n"
        if result.get('highlights'):
            context += f"   Highlights: {', '.join(result['highlights']) if isinstance(result['highlights'], list) else result['highlights']}\n"
        if result.get('amenities'):
            context += f"   Amenities: {', '.join(result['amenities'])}\n"
        if result.get('cuisine'):
            context += f"   Cuisine: {result['cuisine']}\n"
        if result.get('duration_hours'):
            context += f"   Duration: {result['duration_hours']} hours\n"
        
        context += "\n"
    
    # Format conversation history
    history_text = ""
    if conversation_history:
        history_text = "CONVERSATION HISTORY:\n"
        for msg in conversation_history[-4:]:  # Last 4 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_text += f"{role.upper()}: {content}\n"
        history_text += "\n"
    
    # Format preferences
    pref_text = ""
    if preferences:
        pref_text = "USER PREFERENCES:\n"
        if preferences.get('budget'):
            pref_text += f"- Budget: {preferences['budget']}\n"
        if preferences.get('interests'):
            pref_text += f"- Interests: {', '.join(preferences['interests'])}\n"
        pref_text += "\n"
    
    # Build full prompt
    prompt = f"""{SYSTEM_PROMPT}

{history_text}{pref_text}{context}

USER QUESTION: {user_message}

Provide a helpful, conversational response with specific recommendations from the available options. Explain why each recommendation matches the user's needs."""
    
    return prompt


def chat(user_message, search_results, conversation_history=None, preferences=None):
    """Generate conversational response using Gemini"""
    try:
        # Build prompt with RAG context
        prompt = build_rag_prompt(user_message, search_results, conversation_history, preferences)
        
        # Initialize Gemini model (use correct model name for API)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        # Fallback to raw search results
        fallback = "I found these travel options for you:\n\n"
        for result in search_results[:5]:
            fallback += f"• {result['name']} - {result['description'][:100]}...\n"
        return fallback

def chat_stream(user_message, search_results, conversation_history=None, preferences=None):
    """Generate streaming response using Gemini"""
    try:
        # Build prompt with RAG context
        prompt = build_rag_prompt(user_message, search_results, conversation_history, preferences)
        
        # Initialize Gemini model (use correct model name for API)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate streaming response
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
        
    except Exception as e:
        print(f"Error generating streaming response: {e}")
        yield f"I encountered an error, but here are the search results I found:\n\n"
        for result in search_results[:5]:
            yield f"• {result['name']} - {result['description'][:100]}...\n"

def parse_recommendations(response_text, search_results):
    """Parse structured recommendations from Gemini response"""
    recommendations = []
    
    # Match mentioned items from search results
    for result in search_results:
        if result['name'].lower() in response_text.lower():
            recommendations.append({
                'name': result['name'],
                'type': result['type'],
                'rating': result.get('rating'),
                'price_range': result.get('price_range'),
                'location': result.get('location')
            })
    
    return recommendations


def generate_itinerary(destination, days, preferences, es):
    """Generate day-by-day itinerary using Gemini and search"""
    from modules.search import search_travel_data
    
    try:
        # Search for activities and restaurants in the destination
        city = destination.split(',')[0].strip()
        
        activities = search_travel_data(es, f"activities in {city}", 
                                       filters={'type': 'activity'}, size=15)
        restaurants = search_travel_data(es, f"restaurants in {city}", 
                                        filters={'type': 'restaurant'}, size=10)
        
        # Build itinerary prompt
        prompt = f"""Create a detailed {days}-day itinerary for {destination}.

AVAILABLE ACTIVITIES:
{json.dumps([{'name': a['name'], 'description': a['description'], 'duration': a.get('duration_hours'), 'best_time': a.get('best_time')} for a in activities], indent=2)}

AVAILABLE RESTAURANTS:
{json.dumps([{'name': r['name'], 'description': r['description'], 'cuisine': r.get('cuisine'), 'price': r.get('price_range')} for r in restaurants], indent=2)}

USER PREFERENCES:
{json.dumps(preferences, indent=2)}

Create a day-by-day itinerary with:
- Morning, afternoon, and evening activities
- Restaurant recommendations for meals
- Logical flow considering location proximity and timing
- Estimated times for each activity
- Brief explanation of why each choice fits the user's preferences

Format as:
Day 1:
Morning (9:00 AM): [Activity] - [Why it's recommended]
Lunch (12:30 PM): [Restaurant] - [Why it's recommended]
Afternoon (2:00 PM): [Activity] - [Why it's recommended]
Dinner (7:00 PM): [Restaurant] - [Why it's recommended]

Continue for all {days} days."""

        # Initialize Gemini model (use correct model name for API)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return f"I encountered an error generating the itinerary. Please try again or ask for specific recommendations for {destination}."
