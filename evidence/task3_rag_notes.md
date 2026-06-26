# Task 3: Bilingual RAG Workflow, Guardrails, & Telemetry Notes

This document provides the architectural analysis, design implementations, and telemetry metrics compiled during the setup of the Bilingual RAG (Retrieval-Augmented Generation) Workflow for the AL ROUF LED microservice.

---

## 1. Approach

The RAG workflow is constructed to be robust, performant, and fully offline-friendly.

- **ChromaDB as Vector Storage**: ChromaDB was selected as the vector store. By utilizing Chroma's default sentence-transformers embedding engine, all document indexing and similarity search operations run locally on the machine. This avoids external API keys, runtime costs, and dependency on internet connectivity during database queries.
- **Gemini 3.1 Flash Lite**: Serves as the language generation model. It is designed for low-latency and cost-effective operations, making it highly suitable for enterprise-scale customer support and real-time document search integrations.

---

## 2. Bilingual Strategy

The Quotation Engine must serve a diverse client base, requiring seamless bilingual operations:

- **Language Detection & Auto-Response**: Rather than using external translation services, the Gemini model is instructed via the system prompt to dynamically detect the query language (English or Arabic) and respond in that same language.
- **Context Preservation**: The system prompt ensures that terminology, specifications, and formatting (such as bullet points, metric measurements, and product codes) are kept consistent. The context remains in its original language, and the LLM translates the extracted concepts directly to formulate a cohesive bilingual answer.

---

## 3. Guardrails & Safety

To operate safely in a commercial setting, strict guardrails are enforced to eliminate hallucinations and contain out-of-scope interactions:

- **Clean Refusal Directive**: The system prompt contains a strict fallback instruction: if the retrieved context does not contain the exact data required to fulfill the user's query, the model must cleanly refuse to answer.
- **Standardized Refusal Template**: The model is forbidden from guessing, speculating, or pulling training data from outside sources. It must output exactly:
  * *English*: `"I am sorry, but I can only answer questions based on the provided AL ROUF LED documentation."`
  * *Arabic*: A direct Arabic translation of the refusal string.
- **Out-of-Scope Testing**: This behavior was successfully verified using an out-of-scope query test case ("What is the recipe for biryani?"). The RAG workflow intercepted the question and returned the exact refusal string.

---

## 4. Citations & Metrics

Telemetry and audit logs are embedded directly into the RAG workflow payload:

- **Citation Tracking**: Document chunk metadata is stored in ChromaDB (specifically tracking `source` filename). Upon similarity search, the filenames are extracted and parsed into a unique `"citations"` array returned to the user alongside the text, verifying the lineage of the response.
- **Latency Tracking**: Python's `time` module monitors the exact execution time from the moment the user sends the query to the completion of the LLM generation.
- **Cost Estimation**: The `usage_metadata` from the Gemini API response object is parsed to extract input and output token counts. Costs are calculated using commercial parameters:
  - Input tokens: **$0.075 / 1,000,000 tokens**
  - Output tokens: **$0.30 / 1,000,000 tokens**
  - Combined cost and token counts are returned in a `"telemetry"` dictionary.

---

## 5. AI Assistance Disclosure

This phase was completed via an integrated pair-programming workflow:

- **AI Agent (Google Antigravity)**: Responsible for drafting database setup scripts (`rag/ingest.py`), implementing similarity search wrappers, wrapping the time tracking and cost estimation metrics, and executing git version control automation.
- **Candidate**: Provided overall design blueprints, defined schema constraints (e.g., prompt refusal strings, citation schemas, and target models), conducted local tests, and managed prompt engineering logic.
