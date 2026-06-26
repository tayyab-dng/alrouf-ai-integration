# Task 2: Architectural Evidence & Notes - Quotation Engine

This document outlines the design decisions, trade-offs, security practices, and AI assistance disclosure for the AL ROUF LED Assessment Quotation Engine microservice.

---

## 1. Approach

The Quotation Engine microservice is designed using a lean, high-performance architecture optimized for rapid development, testing, and offline-first environments.

- **FastAPI**: Chosen as the primary web framework due to its asynchronous runtime (ASGI), native OpenAPI generation (Swagger UI and Redoc), and automatic validation of query, path, and body payloads. It minimizes boilerplate code while maintaining production-grade speed.
- **Offline-Friendly mock storage**: Instead of relying on a remote database service or cloud instance, the project persists quotes in a local JSON file (`app/mocks/mock_quotes.json`). This ensures that the application can run in environments without internet connectivity, local database installations, or cloud credentials.

---

## 2. Decisions & Trade-offs

During the design and prototyping phases, several trade-offs were made regarding storage and portability:

- **Local JSON File vs. Relational Database (e.g., PostgreSQL/SQLite)**:
  - *Simplicity & Portability (Chosen)*: Using a local JSON file eliminates installation, schema migrations, and connection string setup. The entire project remains portable and can be checked out and run immediately, which is ideal for technical assessments.
  - *Concurrency & Scale (Trade-off)*: A raw JSON file read/write approach suffers from poor concurrent write safety (race conditions) and high memory/IO cost as the database grows, compared to relational engines which offer ACID compliance and transactional locks.
  - *Mitigation*: For the scope of this mock assessment, simplicity was prioritized. The code uses clean python file handles to write to the mock file. If transition to a database is required in the future, the JSON operations are encapsulated in simple helper functions (`read_mock_quotes` and `write_mock_quotes`), making a future transition to SQLAlchemy/Postgres straightforward.

---

## 3. Maintainability & Security Hygiene

To ensure the microservice meets industry standards, the following software engineering practices were applied:

- **Pydantic V2 Validation**: All request and response structures are validated using Pydantic models (e.g., `QuoteItem`, `CreateQuoteRequest`, `Quotation`). This guarantees that incoming data has correct types, non-empty structures, positive values (e.g., `quantity > 0` and `unit_price >= 0.0`), preventing invalid data from corrupting the JSON mock store.
- **Security Configuration via `.env`**: In alignment with Twelve-Factor App principles, secrets (such as the simulated API key and local database string) are externalized using `.env`. A `.env.example` file is included in version control as a template, while the actual `.env` file containing secrets is strictly ignored by Git.
- **Test Isolation**: A custom pytest fixture (`backup_and_restore_mock_quotes`) was written to backup the mock data file before each test runs and restore it during the teardown phase. This prevents test runs from polluting production mock data and keeps the automated test suite completely idempotent.

---

## 4. AI Assistance Disclosure

This project was built under a pair programming paradigm between the candidate and an AI coding agent:

- **AI Agent (Google Antigravity)**: Utilized for executing low-level tasks, including directory structure scaffolding, boilerplate router creation, writing the pytest client test suite, configuring `.dockerignore` and `Dockerfile`, and fixing deprecation warnings.
- **Candidate**: Led and directed the architectural design, dictated the routing and endpoint schemas, orchestrated the workflow steps, performed manual oversight, and engaged in prompt engineering to steer the development process.
