# AI-Powered Travel Assistant v2.0

An intelligent conversational travel planning application featuring multi-agent architecture with MCP, A2A, and AP2 protocols. Built for the AI Accelerate Hackathon using Elastic's hybrid search and Google Cloud's Gemini AI.

## 🎯 Hackathon Challenge

This project addresses the **Elastic Challenge**: Building the future of AI-powered search using Elastic's hybrid search capabilities and Google Cloud's generative AI tools to create a conversational solution that transforms how people plan their travels.

## ✨ Key Features

### v2.0 Enhanced Features
- 🤖 **Multi-Agent Architecture**: Specialized agents for flights, payments, and orchestration
- 🔌 **MCP Protocol**: Model Context Protocol for flight data integration
- 🔄 **A2A Protocol**: Agent-to-Agent communication for coordinated workflows
- 💳 **AP2 Protocol**: Agent Payment Protocol for transaction processing
- 🎯 **Conversational UI**: Natural language booking workflow
- ☁️ **Cloud Deployment**: Production-ready on Google Cloud Run

### Core Features
- 🔍 **Hybrid Search**: BM25 keyword search + k-NN vector search with RRF
- 💬 **Conversational AI**: Natural language interaction powered by Google Gemini
- 🗺️ **Intelligent Itinerary Generation**: Multi-step agentic workflow
- 🎯 **Personalized Recommendations**: RAG for context-aware suggestions
- 📊 **Preference Learning**: Extracts and remembers user preferences

## 🏗️ Architecture

### Multi-Agent System

```
User Interface
      ↓
Orchestrator Agent
      ↓
├─→ Flight Agent (MCP Protocol)
│   └─→ Flight MCP Server
│
├─→ Payment Agent (AP2 Protocol)
│   └─→ Payment Processing
│
└─→ Base Agent (A2A Protocol)
    └─→ Agent Communication
```

### Technology Stack

**Backend:**
- Python 3.10+
- Flask (Web Framework)
- SQLAlchemy (ORM)
- Redis (Caching & Sessions)

**AI & Search:**
- Google Gemini 2.5 Flash (Conversational AI)
- Google Vertex AI (Embeddings)
- Elasticsearch 8.x (Hybrid Search)

**Protocols:**
- MCP (Model Context Protocol)
- A2A (Agent-to-Agent)
- AP2 (Agent Payment Protocol)

**Infrastructure:**
- Google Cloud Run (Serverless Deployment)
- Docker (Containerization)
- Cloud Build (CI/CD)

## 🚀 Quick Start

### Option 1: Use Live Demo

Visit the deployed application:
```
https://travel-assistant-v2-640958026619.us-central1.run.app
```

Try these queries:
1. "I want to travel to Tokyo in December"
2. "Show me flights from San Francisco to Tokyo"
3. "Book the cheapest flight"
4. "Process payment"

### Option 2: Run Locally

#### Prerequisites
- Python 3.10+
- Docker (optional, for Elasticsearch)
- Google Cloud account with Vertex AI enabled

#### Setup

1. **Clone and Install**
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Environment**

Create `.env` file:
```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-gemini-api-key

# Elasticsearch (optional for local dev)
ELASTICSEARCH_URL=https://your-elasticsearch-url
ELASTICSEARCH_API_KEY=your-es-api-key

# Model Configuration
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-004

# Application Configuration
PORT_V2=5001
DATABASE_URL=sqlite:///travel_assistant.db
REDIS_URL=redis://localhost:6379
```

3. **Run the Application**

```bash
# Run v2.0 (Enhanced with protocols)
python app_v2.py

# Or run v1.0 (Basic version)
python app.py
```

Open browser to `http://localhost:5001` (v2) or `http://localhost:5000` (v1)

## 📁 Project Structure

```
.
├── app_v2.py                   # v2.0 Flask application with protocols
├── app.py                      # v1.0 Flask application
│
├── agents/                     # Multi-agent system
│   ├── base_agent.py          # Base agent with A2A protocol
│   ├── orchestrator.py        # Main orchestration agent
│   ├── flight_agent.py        # Flight booking agent
│   └── payment_agent.py       # Payment processing agent (AP2)
│
├── mcp_servers/               # MCP Protocol servers
│   ├── base_server.py         # Base MCP server
│   └── flight_server.py       # Flight data MCP server
│
├── shared/                    # Shared utilities
│   ├── protocols.py           # Protocol definitions (MCP, A2A, AP2)
│   ├── database.py            # Database models and setup
│   ├── redis_client.py        # Redis connection
│   └── message_queue.py       # Message queue for A2A
│
├── modules/                   # v1.0 modules
│   ├── elasticsearch_setup.py # ES connection
│   ├── data_loader.py         # Data loading
│   ├── search.py              # Hybrid search
│   └── agent.py               # Gemini AI agent
│
├── static/                    # Frontend assets
│   ├── app_v2.js              # v2.0 UI logic
│   ├── style_v2.css           # v2.0 styling
│   └── app.js                 # v1.0 UI logic
│
├── templates/                 # HTML templates
│   ├── index_v2.html          # v2.0 interface
│   └── index.html             # v1.0 interface
│
├── data/                      # Sample travel data
│   ├── destinations.json
│   ├── activities.json
│   ├── hotels.json
│   └── restaurants.json
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── deploy.bat                 # Windows deployment script
├── deploy.sh                  # Linux/Mac deployment script
└── README.md                  # This file
```

## 💡 How It Works

### 1. Conversational Workflow

```
User: "I want to fly to Tokyo"
  ↓
Orchestrator Agent
  ↓
Flight Agent (MCP)
  ↓
Flight MCP Server → Search Flights
  ↓
Return Results → User selects flight
  ↓
Payment Agent (AP2) → Process Payment
  ↓
Booking Confirmed
```

### 2. Protocol Implementation

**MCP (Model Context Protocol)**
- Standardized interface for flight data
- Tool registration and execution
- Context management

**A2A (Agent-to-Agent)**
- Message passing between agents
- Task delegation and coordination
- Shared context and state

**AP2 (Agent Payment Protocol)**
- Secure payment processing
- Transaction validation
- Payment status tracking

### 3. Hybrid Search (v1.0)

```
User Query → Vertex AI Embeddings → Elasticsearch
                                    ├─ BM25 Keyword Search
                                    ├─ k-NN Vector Search
                                    └─ RRF Ranking → Top Results
```

## 🎮 Usage Examples

### Example 1: Flight Booking
```
User: "I want to fly from San Francisco to Tokyo on December 1st"
Assistant: [Searches flights via MCP protocol]
          [Shows 5 flight options with prices]
User: "Book the cheapest one"
Assistant: [Initiates booking via Flight Agent]
          [Processes payment via Payment Agent]
          [Confirms booking]
```

### Example 2: Travel Planning
```
User: "Plan a 3-day trip to Kyoto"
Assistant: [Searches destinations and activities]
          [Generates day-by-day itinerary]
          [Suggests hotels and restaurants]
```

### Example 3: Preference Learning
```
User: "I prefer budget-friendly options"
Assistant: [Remembers preference]
          [Filters future recommendations]
          [Shows only $ and $$ options]
```

## 🌐 Deployment

### Deploy to Google Cloud Run

1. **Prerequisites**
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Enable APIs (one-time setup)
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

2. **Configure Environment**
```bash
# Copy .env.example to .env
cp .env.example .env  # Linux/Mac
copy .env.example .env  # Windows

# Edit .env with your credentials
# Required:
#   GOOGLE_CLOUD_PROJECT=your-project-id
#   GOOGLE_API_KEY=your-gemini-api-key
# Optional:
#   ELASTICSEARCH_URL=your-elasticsearch-url
#   ELASTICSEARCH_API_KEY=your-es-api-key
```

3. **Deploy**
```bash
# Windows
.\deploy.bat

# Linux/Mac
chmod +x deploy.sh
./deploy.sh
```

The deployment script will:
- Read configuration from `.env` file
- Build Docker image using Cloud Build
- Deploy to Cloud Run with auto-scaling
- Configure environment variables
- Display the service URL

4. **Get Service URL**
```bash
gcloud run services describe travel-assistant-v2 \
  --region us-central1 \
  --format "value(status.url)"
```

### Configuration

The deployment automatically configures:
- Memory: 2GB
- CPU: 2 cores
- Timeout: 300 seconds
- Max Instances: 10
- Region: us-central1
- Auto-scaling: 0-10 instances
- Environment variables from `.env`

## 📊 Data Sources

### Real Data (Production-Ready)
✅ **Google Gemini AI** - Real AI responses via Vertex AI  
✅ **Elasticsearch** - Real travel data (destinations, hotels, restaurants)  
✅ **User Conversations** - Real user input and preferences  
✅ **Database** - SQLite (local) / Cloud SQL (production)

### Generated Data (Demo)
⚠️ **Flight Search** - Generates realistic flight data on-the-fly  
⚠️ **Payment Processing** - Simulates payment transactions

**Why Generated Data?**
- Perfect for hackathon demo
- No API costs during development
- Consistent, reliable results
- Shows complete architecture
- Easy to swap with real APIs later

### Integrating Real APIs (Production)

**Flight Data - Amadeus API**
```python
from amadeus import Client

amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

flights = amadeus.shopping.flight_offers_search.get(
    originLocationCode='SFO',
    destinationLocationCode='NRT',
    departureDate='2025-12-01',
    adults=2
)
```

**Payments - Stripe**
```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

payment = stripe.PaymentIntent.create(
    amount=120000,  # $1,200 in cents
    currency='usd',
    payment_method=payment_method_id,
    confirm=True
)
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_v2.py
```

### Test Endpoints

**Health Check**
```bash
curl http://localhost:5001/api/health
```

**Chat**
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","conversation_id":"test123"}'
```

**Flight Search**
```bash
curl -X POST http://localhost:5001/api/v2/search-flights \
  -H "Content-Type: application/json" \
  -d '{"origin":"SFO","destination":"NRT","date":"2025-12-01","passengers":2}'
```

## 📝 API Documentation

### v2.0 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Send message, receive AI response |
| `/api/v2/search-flights` | POST | Search flights via MCP |
| `/api/v2/book-flight` | POST | Book flight via Flight Agent |
| `/api/v2/process-payment` | POST | Process payment via Payment Agent |
| `/api/v2/conversation-history` | GET | Get conversation history |

### Request/Response Examples

**Chat Request**
```json
{
  "message": "I want to fly to Tokyo",
  "conversation_id": "user123"
}
```

**Chat Response**
```json
{
  "response": "I can help you find flights to Tokyo...",
  "conversation_id": "user123",
  "agent": "orchestrator"
}
```

## 🏆 Hackathon Highlights

This project showcases:

✅ **Multi-Agent Architecture** - Specialized agents with clear responsibilities  
✅ **Protocol Implementation** - MCP, A2A, and AP2 protocols  
✅ **Elastic Hybrid Search** - BM25 + k-NN with RRF for superior relevance  
✅ **Google Cloud Integration** - Vertex AI embeddings + Gemini conversation  
✅ **Production Deployment** - Live on Cloud Run with auto-scaling  
✅ **Agentic Workflows** - Multi-step reasoning for complex tasks  
✅ **RAG Pattern** - Grounded, accurate responses with source data  
✅ **Real-world Use Case** - Everyday travel planning transformed by AI

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Yes | - |
| `GOOGLE_API_KEY` | Gemini API key | Yes | - |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint | No | - |
| `ELASTICSEARCH_API_KEY` | Elasticsearch API key | No | - |
| `GEMINI_MODEL` | Gemini model name | No | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Vertex AI embedding model | No | `text-embedding-004` |
| `DATABASE_URL` | Database connection string | No | `sqlite:///travel_assistant.db` |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379` |
| `PORT_V2` | Application port | No | `5001` |

## 💰 Cost Estimate

### Free Tier (Included)
- **Cloud Run**: 2M requests/month
- **Gemini API**: 60 requests/minute
- **Cloud Build**: 120 build-minutes/day

### Beyond Free Tier
- **Cloud Run**: ~$0.000024 per request
- **Gemini API**: ~$0.00025 per 1K characters
- **Estimated**: $10-50/month for moderate usage

## 📚 Documentation

- **DEPLOY.md** - Detailed deployment guide
- **.kiro/specs/** - Feature specifications and design docs
- **Code Comments** - Inline documentation throughout codebase

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - Open source for hackathon submission

## 🙏 Acknowledgments

- **Elastic** - For the hybrid search challenge and Elasticsearch
- **Google Cloud** - For Vertex AI and Gemini API
- **AI Accelerate Hackathon** - For the opportunity to build this project

## 📞 Support

For questions or issues:
- Check the logs: `gcloud run services logs tail travel-assistant-v2 --region us-central1`
- View metrics: [Cloud Console](https://console.cloud.google.com/run)
- Review documentation in this README

---

**Built with ❤️ for the AI Accelerate Hackathon**

**Live Demo:** [https://travel-assistant-v2-640958026619.us-central1.run.app](https://travel-assistant-v2-640958026619.us-central1.run.app)
