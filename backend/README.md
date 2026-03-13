# LegalContractAI Backend API

FastAPI backend for AI-powered legal contract drafting, compliance checking, and intelligent analysis. Powered by advanced LLMs (Google Gemini, OpenAI) with RAG (Retrieval-Augmented Generation) capabilities using Pinecone vector database.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` and update with your API key:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📋 API Endpoints

### Health Check

**GET** `/api/health`

Check if API and services are running.

```bash
curl http://localhost:8000/api/health
```

---

### Contract Drafting

**POST** `/api/drafting/draft`

Generate a professional contract using AI.

**Request Body:**
```json
{
  "party_a": "Acme Corporation",
  "party_b": "Example Industries Inc.",
  "jurisdiction": "United States",
  "purpose": "Service Agreement",
  "term": "24 months",
  "requirements": "This is a software development service agreement where Party A will provide web development services to Party B..."
}
```

**Response:**
```json
{
  "drafted_contract": "# SERVICE AGREEMENT\n\nThis Service Agreement...",
  "compliance_report": [],
  "metadata": {
    "parties": [...],
    "jurisdiction": "United States",
    ...
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/drafting/draft \
  -H "Content-Type: application/json" \
  -d '{
    "party_a": "Acme Corp",
    "party_b": "Example Inc",
    "jurisdiction": "United States",
    "requirements": "Create a service agreement for software development"
  }'
```

---

### Compliance Check

**POST** `/api/compliance/check`

Analyze contract for compliance issues.

**Request Body:**
```json
{
  "contract_text": "TERMINATION CLAUSE\n\nEither party may terminate this agreement...",
  "jurisdiction": "United States"
}
```

**Response:**
```json
{
  "drafted_contract": "original contract text",
  "compliance_report": [
    {
      "clause": "Either party may terminate...",
      "risk_level": "medium",
      "fix": "Add specific notice period and termination procedures",
      "citations": ["us_contract_law_basics.md"]
    }
  ],
  "summary": {
    "total_clauses": 5,
    "high_risk": 1,
    "medium_risk": 2,
    "low_risk": 2,
    "overall_assessment": "REVIEW NEEDED"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "Your contract text here...",
    "jurisdiction": "United States"
  }'
```

---

### Structured Report Generation

**POST** `/api/reports/generate`

Produce a richly formatted Markdown report (case summary, loophole analysis, etc.) via server-side prompt engineering.

**Request Body:**
```json
{
  "task_type": "case-summary",
  "content": "Paste raw facts, clauses, or instructions here",
  "jurisdiction": "Optional context"
}
```

**Response:**
```json
{
  "task_type": "case-summary",
  "report_markdown": "# Case Snapshot...",
  "metadata": {
    "jurisdiction": "United States"
  }
}
```

---

## 🏗️ Architecture

### Service 1: Contract Drafting

```
Request → DraftingOrchestrator → ingestion_agent → drafting_agent → LLM → Response
```

**Agents Used:**
- ✅ `ingestion_agent` - Normalizes input data
- ✅ `drafting_agent` - Generates contract structure
- ✅ LLM (Gemini/OpenAI) - Generates professional contract content
- ✅ `template_agent` - Applies contract templates

**Includes:** Template-based generation, compliance integration, metadata extraction

---

### Service 2: Compliance Check

```
Request → ComplianceOrchestrator → clause_agent → [for each clause]:
  RAG retrieval (Pinecone) → compliance_agent (LLM analysis) → risk_agent
  → structure_agent → Report generator → JSON Response
```

**Agents Used:**
- ✅ `clause_agent` - Splits contract into separate clauses
- ✅ `compliance_agent` - Analyzes clauses using RAG-enhanced LLM prompts
- ✅ `risk_agent` - Classifies risk level (low/medium/high)
- ✅ `structure_agent` - Organizes analysis results
- ✅ RAG (Pinecone) - Retrieves relevant legal statutes and precedents

**Includes:** Semantic search via Pinecone, jurisdiction-specific compliance, risk scoring, detailed remediation suggestions

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── agents/              # AI Agents for legal tasks
│   │   ├── ingestion_agent.py           # Input normalization
│   │   ├── clause_agent.py              # Contract clause splitting
│   │   ├── compliance_agent.py          # Compliance analysis
│   │   ├── risk_agent.py                # Risk classification
│   │   ├── drafting_agent.py            # Contract generation
│   │   ├── structure_agent.py           # Result structuring
│   │   ├── template_agent.py            # Template handling
│   │   ├── merge_agent.py               # Document merging
│   │   ├── state.py                     # Agent state management
│   │   ├── compliance/                  # Compliance orchestration
│   │   │   ├── orchestrator.py
│   │   │   └── ...
│   │   └── drafting/                    # Drafting orchestration
│   │       ├── orchestrator.py
│   │       └── ...
│   ├── api/                 # API Route Handlers (9 endpoints)
│   │   ├── health.py        # Health check endpoint
│   │   ├── drafting.py      # Contract drafting endpoint
│   │   ├── compliance.py    # Compliance check endpoint
│   │   ├── reports.py       # Report generation endpoint
│   │   ├── analysis.py      # General analysis endpoint
│   │   ├── research.py      # Research query endpoint
│   │   ├── summarization.py # Document summarization endpoint
│   │   ├── chat.py          # Interactive chat endpoint
│   │   └── usage.py         # Usage analytics endpoint
│   ├── llms/                # LLM Client Implementations
│   │   ├── gemini_client.py       # Google Gemini integration
│   │   ├── openai_client.py       # OpenAI integration
│   │   ├── hybrid_client.py       # Hybrid LLM routing
│   │   └── prompts/               # Prompt templates
│   ├── services/            # Business Logic Services
│   │   ├── draft_service.py       # Contract draft service
│   │   ├── compliance_service.py  # Compliance checking service
│   │   ├── insight_service.py     # Insight generation service
│   │   ├── supabase_service.py    # Supabase integration
│   │   └── encryption.py          # Message encryption
│   ├── RAG/                 # Retrieval-Augmented Generation
│   │   └── pinecone_store.py      # Pinecone vector database integration
│   ├── schemas/             # Pydantic Data Models
│   │   └── __init__.py
│   ├── utils/               # Utility Functions
│   │   ├── rate_limiter.py
│   │   └── __init__.py
│   └── pdf_templates/       # Contract PDF Templates by Type
│       ├── ea/  ├── ica/  ├── la/  ├── msa/
│       ├── nca/ ├── nda/  ├── pa/  └── sow/
├── scripts/                 # Utility Scripts
│   ├── ingest_data.py
│   ├── setup_pinecone.py
│   ├── test_rag_manual.py
│   └── ...
├── legal_texts/             # Legal Reference Documents
│   └── (various .md and .txt files)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── Dockerfile               # Docker containerization
├── Procfile                 # Heroku deployment
└── README.md               # Backend documentation
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
OPENAI_API_KEY=your_openai_api_key_here (optional)

# RAG Configuration (Pinecone)
PINCONE_API_KEY=your_pinecone_api_key
PINCONE_INDEX=your_pinecone_index_name
PINCONE_ENV=your_pinecone_environment

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Encryption
CHAT_ENCRYPTION_KEY_V1=your_encryption_key_for_chat

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### Legal Reference Files

Add legal reference documents to `legal_texts/` directory for RAG-enhanced analysis:

```bash
legal_texts/
├── us_contract_law_basics.md      # US contract law principles
├── gdpr_compliance.txt            # GDPR requirements
├── hipaa_requirements.md          # HIPAA compliance rules
├── california_law.md              # California-specific statutes
├── employment_law.md              # Employment contract law
└── ...
```

Supported formats: `.txt`, `.md`

**Note**: Use `scripts/setup_pinecone.py` to ingest these documents into Pinecone for RAG retrieval.

---

## 🧪 Testing

### Test with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Draft contract
curl -X POST http://localhost:8000/api/drafting/draft \
  -H "Content-Type: application/json" \
  -d @test_draft.json

# Check compliance
curl -X POST http://localhost:8000/api/compliance/check \
  -H "Content-Type: application/json" \
  -d @test_compliance.json
```

### Test with Python

```python
import requests

# Draft contract
response = requests.post(
    "http://localhost:8000/api/drafting/draft",
    json={
        "party_a": "Test Corp",
        "party_b": "Example Inc",
        "jurisdiction": "United States",
        "requirements": "Create a simple service agreement"
    }
)
print(response.json())

# Check compliance
response = requests.post(
    "http://localhost:8000/api/compliance/check",
    json={
        "contract_text": "Your contract text here...",
        "jurisdiction": "United States"
    }
)
print(response.json())
```

---

## 🔍 API Response Formats

### Success Response (Drafting)
```json
{
  "drafted_contract": "string (Markdown)",
  "compliance_report": [],
  "metadata": {
    "parties": [...],
    "jurisdiction": "string",
    "purpose": "string",
    "term": "string"
  }
}
```

### Success Response (Compliance)
```json
{
  "drafted_contract": "string (original)",
  "compliance_report": [
    {
      "clause": "string",
      "risk_level": "low|medium|high",
      "fix": "string",
      "citations": ["string"]
    }
  ],
  "summary": {
    "total_clauses": 0,
    "high_risk": 0,
    "medium_risk": 0,
    "low_risk": 0,
    "overall_assessment": "string"
  }
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

---

## 🚦 Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

---

## 📚 Documentation

- **Agent Documentation**: `app/agents/README.md`
- **Agent Examples**: `app/agents/examples.py`
- **Quick Start**: `QUICKSTART.md`

---

## 🔗 Integration with Frontend

The frontend should call these endpoints:

```typescript
// Contract Drafting
const response = await fetch('http://localhost:8000/api/drafting/draft', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    party_a: "Acme Corp",
    party_b: "Example Inc",
    jurisdiction: "United States",
    requirements: "..."
  })
});

// Compliance Check
const response = await fetch('http://localhost:8000/api/compliance/check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    contract_text: "...",
    jurisdiction: "United States"
  })
});

// Structured Insight
const response = await fetch('http://localhost:8000/api/reports/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_type: 'case-summary',
    content: 'Facts or clauses to analyze'
  })
});
```

Set the frontend environment variable `VITE_API_BASE_URL` to point at the backend origin (e.g., `http://localhost:8000`) so every AI page proxies requests through the API instead of calling Gemini directly.
```

---

## 🛠️ Development

### Run in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View Logs

Logs are printed to console. Configure log level in `.env`:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

---

## 📝 Implementation Notes

- **RAG**: Fully implemented using Pinecone for semantic search and retrieval
- **LLM**: Supports both Google Gemini and OpenAI with intelligent fallback routing
- **Vector Embeddings**: Uses Pinecone's server-side embedding for optimal performance
- **Legal Knowledge**: Comprehensive legal text library for RAG context retrieval
- **Async Architecture**: All agents and endpoints are fully async for maximum performance
- **Compliance**: Supports multiple jurisdictions (US, India, EU, etc.)
- **Extensibility**: Modular agent design allows easy addition of new capabilities
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Encryption**: Message-level encryption for sensitive legal data

---

## ✅ Production-Ready Features

All components are fully implemented and battle-tested:
- ✅ **9 AI Agents** - Drafting, Compliance, Risk, Clause, Ingestion, Merge, Structure, Template, and more
- ✅ **9 API Endpoints** - Drafting, Compliance, Reports, Analysis, Research, Summarization, Chat, Usage, Health
- ✅ **Dual LLM Support** - Gemini and OpenAI with hybrid routing
- ✅ **RAG Integration** - Pinecone vector database with semantic search
- ✅ **Data Persistence** - Supabase with encrypted storage
- ✅ **Request/Response Validation** - Pydantic schemas for all endpoints
- ✅ **Error Handling** - Comprehensive error reporting
- ✅ **CORS Configuration** - Production-ready security settings
- ✅ **API Documentation** - Auto-generated Swagger UI and ReDoc
- ✅ **Deployment Ready** - Docker, Heroku, and Railway configurations included

---

## 🎉 Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Set your `GEMINI_API_KEY` in `.env`
3. Run: `python -m app.main`
4. Visit: http://localhost:8000/docs

**Your backend is ready!** 🚀
