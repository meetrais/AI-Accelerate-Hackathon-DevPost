import os
from vertexai.language_models import TextEmbeddingModel
from dotenv import load_dotenv

load_dotenv()

def get_query_embedding(text, model_name='text-embedding-004'):
    """Generate embedding for search query"""
    try:
        model = TextEmbeddingModel.from_pretrained(model_name)
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None

def build_hybrid_search_query(query_text, query_embedding, filters=None, size=10):
    """Build Elasticsearch hybrid search query combining keyword and vector search"""
    
    # Build the query with both keyword and vector search
    query = {
        "size": size,
        "query": {
            "bool": {
                "should": [
                    # Keyword search
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["name^3", "description^2", "highlights", "specialties"],
                            "type": "best_fields",
                            "boost": 1.0
                        }
                    },
                    # Vector similarity search
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_embedding}
                            },
                            "boost": 1.0
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }
    
    # Add filters if provided
    if filters:
        filter_clauses = []
        
        if 'price_range' in filters:
            filter_clauses.append({"term": {"price_range": filters['price_range']}})
        
        if 'categories' in filters:
            filter_clauses.append({"terms": {"categories": filters['categories']}})
        
        if 'type' in filters:
            filter_clauses.append({"term": {"type": filters['type']}})
        
        if 'city' in filters:
            filter_clauses.append({"term": {"location.city": filters['city']}})
        
        if 'country' in filters:
            filter_clauses.append({"term": {"location.country": filters['country']}})
        
        if filter_clauses:
            query["query"]["bool"]["filter"] = filter_clauses
    
    return query


def execute_search(es, query_text, filters=None, index_name='travel_data', size=10):
    """Execute hybrid search against Elasticsearch"""
    try:
        # Generate query embedding
        query_embedding = get_query_embedding(query_text)
        
        if not query_embedding:
            print("Warning: Could not generate embedding, falling back to keyword search only")
            # Fallback to keyword-only search
            query = {
                "size": size,
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["name^3", "description^2", "highlights", "specialties"]
                    }
                }
            }
        else:
            # Build hybrid search query
            query = build_hybrid_search_query(query_text, query_embedding, filters, size)
        
        # Execute search
        response = es.search(index=index_name, body=query)
        return response
        
    except Exception as e:
        print(f"Search error: {e}")
        raise

def format_search_results(response):
    """Format Elasticsearch results for Gemini context"""
    hits = response.get('hits', {}).get('hits', [])
    
    if not hits:
        return []
    
    formatted_results = []
    
    for hit in hits:
        source = hit['_source']
        result = {
            'id': source.get('id'),
            'type': source.get('type'),
            'name': source.get('name'),
            'description': source.get('description'),
            'location': source.get('location', {}),
            'price_range': source.get('price_range'),
            'rating': source.get('rating'),
            'categories': source.get('categories', []),
            'score': hit.get('_score', 0)
        }
        
        # Add type-specific fields
        if source.get('highlights'):
            result['highlights'] = source['highlights']
        if source.get('amenities'):
            result['amenities'] = source['amenities']
        if source.get('cuisine'):
            result['cuisine'] = source['cuisine']
        if source.get('specialties'):
            result['specialties'] = source['specialties']
        if source.get('duration_hours'):
            result['duration_hours'] = source['duration_hours']
        if source.get('best_time'):
            result['best_time'] = source['best_time']
        
        formatted_results.append(result)
    
    return formatted_results

def search_travel_data(es, query_text, filters=None, size=10):
    """Main search function - execute and format results"""
    try:
        response = execute_search(es, query_text, filters, size=size)
        results = format_search_results(response)
        
        if not results:
            print(f"No results found for query: {query_text}")
        else:
            print(f"Found {len(results)} results for query: {query_text}")
        
        return results
        
    except Exception as e:
        print(f"Error in search_travel_data: {e}")
        return []
