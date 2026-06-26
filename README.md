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
│   ├── routers/           # Endpoint routing (future phases)
│   └── mocks/             # Local offline mock data
│       └── mock_quotes.json
├── .env.example           # Environment variable placeholders
├── .gitignore             # Python Git ignore rules
├── requirements.txt       # Python dependencies
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
Copy `.env.example` to `.env` and adjust values:
```bash
cp .env.example .env
```

### 5. Run the application
```bash
uvicorn app.main:app --reload
```
The API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
