# AL ROUF LED Assessment - Quotation Engine

This microservice acts as the Quotation Engine for the AL ROUF LED Assessment. It is designed to run completely offline-friendly, providing mock services for managing lighting equipment quotations.

## Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Testing**: [Pytest](https://docs.pytest.org/)

## Directory Structure
```
alrouf-ai-integration/
├── app/
│   ├── main.py            # Entrypoint & Health-check endpoint
│   ├── routers/           # Quotations endpoint router logic
│   └── mocks/             # Local offline mock data (mock_quotes.json)
├── tests/
│   └── test_quotations.py # Pytest automated API testing suite
├── rag/
│   ├── data/              # Local markdown product documents
│   ├── db/                # Local persistent ChromaDB index files (ignored by Git)
│   ├── ingest.py          # Script to chunk and ingest data into vector DB
│   └── workflow.py        # Bilingual RAG query workflow (Chroma + Gemini 3.1 Flash Lite)
├── automation/
│   ├── sample_rfq_payload.json      # Structured mock payload for inbound webhooks
│   ├── mock_crm_template.csv        # Matching CRM structure template
│   ├── make_workflow_architecture.md # Workflow layout description
│   └── trigger_webhook.py           # Webhook POST trigger automation script
├── .env.example           # Environment variable placeholders
├── .gitignore             # Git ignore patterns
├── Dockerfile             # Docker container configuration
├── requirements.txt       # Frozen Python dependencies
└── README.md              # Project documentation
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd alrouf-ai-integration
```

### 2. Set up virtual environment
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Copy `.env.example` to `.env` and set variables (including `GEMINI_API_KEY` and `WEBHOOK_URL`):
```bash
cp .env.example .env
```

### 5. Run the FastAPI application
```bash
uvicorn app.main:app --reload
```
The API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Running the Automated Test Suite

To execute the Pytest test suite locally:
```bash
pytest
```
*Note: The test suite includes a custom automatic backup/restore fixture, ensuring that test queries do not pollute the production mock quotes database.*

---

## Running the Bilingual RAG Workflow (Task 3)

The RAG workflow queries a local ChromaDB collection and generates responses in the language matching the user's query (English/Arabic) using Gemini 3.1 Flash Lite.

### 1. Ingest documents into ChromaDB
```bash
python rag/ingest.py
```
This loads and tokenizes the product specifications in `rag/data/` and saves the indexes in `rag/db/` offline.

### 2. Query the RAG workflow
```bash
python rag/workflow.py
```
This runs a test block executing English, Arabic, and out-of-scope query containment (refusal template) tests with printed latencies, token counts, and cost metrics.

---

## Running the Webhook Automation (Task 1)

To send the mock RFQ payload (`sample_rfq_payload.json`) to the listening Make.com webhook scenario:
```bash
python automation/trigger_webhook.py
```

---

## Docker Setup

To package and run the application inside a containerized Docker environment:

### 1. Build the Docker image
```bash
docker build -t alrouf-quotation-api .
```

### 2. Run the Docker container
```bash
docker run -p 8000:8000 alrouf-quotation-api
```
Once running, you can access the API endpoints and Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).
