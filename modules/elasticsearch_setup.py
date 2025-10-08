import os
import time
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

def get_elasticsearch_client():
    """Connect to Elasticsearch with retry logic"""
    es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    es_api_key = os.getenv('ELASTICSEARCH_API_KEY')
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if es_api_key:
                es = Elasticsearch(es_url, api_key=es_api_key)
            else:
                es = Elasticsearch(es_url)
            
            if es.ping():
                print(f"✓ Connected to Elasticsearch at {es_url}")
                return es
            else:
                raise ConnectionError("Elasticsearch ping failed")
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"✗ Failed to connect to Elasticsearch after {max_retries} attempts")
                raise

def create_travel_index(es, index_name='travel_data'):
    """Create index with mappings for text and vector fields"""
    
    if es.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Deleting...")
        es.indices.delete(index=index_name)
    
    mappings = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "type": {"type": "keyword"},
                "name": {"type": "text"},
                "description": {"type": "text"},
                "location": {
                    "properties": {
                        "country": {"type": "keyword"},
                        "city": {"type": "keyword"},
                        "region": {"type": "keyword"}
                    }
                },
                "price_range": {"type": "keyword"},
                "rating": {"type": "float"},
                "categories": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                },
                "best_season": {"type": "keyword"},
                "highlights": {"type": "text"},
                "amenities": {"type": "keyword"},
                "cuisine": {"type": "keyword"},
                "specialties": {"type": "text"},
                "duration_hours": {"type": "float"},
                "best_time": {"type": "keyword"}
            }
        }
    }
    
    es.indices.create(index=index_name, body=mappings)
    print(f"✓ Created index '{index_name}' with mappings")
    return True

def check_index_exists(es, index_name='travel_data'):
    """Check if index exists"""
    return es.indices.exists(index=index_name)
