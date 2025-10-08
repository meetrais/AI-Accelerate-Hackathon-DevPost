import json
import os
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from dotenv import load_dotenv

load_dotenv()

def initialize_vertex_ai():
    """Initialize Vertex AI with project credentials"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    aiplatform.init(project=project_id)
    print(f"✓ Initialized Vertex AI for project: {project_id}")

def load_json_data(file_path):
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} records from {file_path}")
        return data
    except Exception as e:
        print(f"✗ Error loading {file_path}: {e}")
        return []

def generate_embeddings_batch(texts, model_name='text-embedding-004'):
    """Generate embeddings for a batch of texts using Vertex AI"""
    try:
        model = TextEmbeddingModel.from_pretrained(model_name)
        embeddings = model.get_embeddings(texts)
        return [emb.values for emb in embeddings]
    except Exception as e:
        print(f"✗ Error generating embeddings: {e}")
        return None

def load_all_travel_data():
    """Load all travel data files"""
    data_dir = 'data'
    all_data = []
    
    files = ['destinations.json', 'activities.json', 'hotels.json', 'restaurants.json']
    
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            data = load_json_data(file_path)
            all_data.extend(data)
        else:
            print(f"⚠ File not found: {file_path}")
    
    print(f"✓ Total records loaded: {len(all_data)}")
    return all_data

def prepare_documents_with_embeddings(data, batch_size=5):
    """Prepare documents with embeddings for indexing"""
    print(f"Generating embeddings for {len(data)} documents...")
    
    documents = []
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        texts = [doc['description'] for doc in batch]
        
        try:
            embeddings = generate_embeddings_batch(texts)
            
            if embeddings:
                for doc, embedding in zip(batch, embeddings):
                    doc['embedding'] = embedding
                    documents.append(doc)
                print(f"  Processed {len(documents)}/{len(data)} documents")
            else:
                print(f"  Skipping batch {i//batch_size + 1} due to embedding error")
                
        except Exception as e:
            print(f"  Error processing batch: {e}")
            continue
    
    print(f"✓ Generated embeddings for {len(documents)} documents")
    return documents


def bulk_index_documents(es, documents, index_name='travel_data'):
    """Bulk index documents to Elasticsearch"""
    from elasticsearch.helpers import bulk
    
    actions = [
        {
            "_index": index_name,
            "_id": doc['id'],
            "_source": doc
        }
        for doc in documents
    ]
    
    try:
        success, failed = bulk(es, actions, raise_on_error=False)
        print(f"✓ Indexed {success} documents successfully")
        if failed:
            print(f"⚠ Failed to index {len(failed)} documents")
        return success
    except Exception as e:
        print(f"✗ Bulk indexing error: {e}")
        return 0

def run_data_pipeline():
    """Run the complete data loading pipeline"""
    from modules.elasticsearch_setup import get_elasticsearch_client, create_travel_index
    
    print("\n=== Starting Data Loading Pipeline ===\n")
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Connect to Elasticsearch
    es = get_elasticsearch_client()
    
    # Create index
    create_travel_index(es)
    
    # Load data
    data = load_all_travel_data()
    
    if not data:
        print("✗ No data to index")
        return
    
    # Generate embeddings
    documents = prepare_documents_with_embeddings(data)
    
    if not documents:
        print("✗ No documents with embeddings to index")
        return
    
    # Index to Elasticsearch
    indexed_count = bulk_index_documents(es, documents)
    
    print(f"\n=== Pipeline Complete: {indexed_count} documents indexed ===\n")

if __name__ == "__main__":
    run_data_pipeline()
