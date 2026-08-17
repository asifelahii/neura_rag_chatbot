# Neura RAG Chatbot

AI-powered chatbot microservice for the Neura Solutions Limited website.

The service is built with **Python, FastAPI, and Google Gemini**. It currently works as a general-purpose conversational assistant and is designed so that a Neura-specific RAG knowledge base can be added later without changing the public chat API.

---

## Overview

The chatbot is intended to be integrated into the Neura Solutions Limited website so visitors can ask questions and receive AI-assisted responses.

The current version can:

- answer general software and technology questions
- maintain multi-turn conversations
- understand follow-up questions using conversation history
- avoid inventing unverified Neura-specific information
- operate without a knowledge base
- support a RAG knowledge base later through the existing architecture
- expose the chatbot through a REST API
- be tested through FastAPI Swagger documentation

The RAG knowledge base is **not implemented yet**.

---

## Current Architecture

```text
Website Visitor
      |
      v
POST /api/v1/chat
      |
      v
FastAPI
      |
      v
Conversation Store
      |
      v
Knowledge Retriever
      |
      +---- RAG disabled ----> No additional context
      |
      +---- RAG enabled -----> Knowledge-base context
      |
      v
Gemini Service
      |
      v
Google Gemini API
      |
      v
Structured API Response
```

At the moment:

```text
RAG_ENABLED=false
```

So the chatbot follows this flow:

```text
User
  |
  v
FastAPI
  |
  v
Conversation History
  |
  v
Gemini
  |
  v
Response
```

Later, when the knowledge base is implemented:

```text
User
  |
  v
FastAPI
  |
  v
Conversation History
  |
  v
RAG Retriever
  |
  v
Neura Knowledge Base
  |
  v
Relevant Context
  |
  v
Gemini
  |
  v
Grounded Response
```

---

## Technology Stack

- Python 3.12+
- FastAPI
- Uvicorn
- Google GenAI SDK
- Google Gemini
- Pydantic
- Pydantic Settings
- python-dotenv
- GitHub Codespaces for development

---

## Current Features

### API

- FastAPI-based REST API
- Health check endpoint
- Chat endpoint
- Swagger/OpenAPI documentation
- Request validation
- Structured JSON responses

### AI

- Gemini API integration
- Neura-specific system instructions
- General software and technology assistance
- Multi-turn conversation support
- Conversation context support
- Guardrails against unverified Neura-specific claims

### Conversation Management

- Unique conversation IDs
- In-memory conversation history
- Maximum conversation history limit
- Automatic inactivity expiration
- Invalid conversation ID handling

### Configuration

- Central application configuration
- Environment variable support
- Secure Gemini API key handling
- Configurable Gemini model
- Configurable RAG mode
- Configurable conversation limits

### Security and API Protection

- Gemini API key stored outside source code
- `.env` excluded from Git
- `.env.example` provided for developers
- CORS restricted to approved frontend origins
- Safe public error responses
- Internal server-side error logging

### RAG Preparation

- Knowledge retriever abstraction
- RAG can be enabled or disabled through configuration
- Chat endpoint does not depend directly on a specific vector database
- Future knowledge-base implementation can be added without redesigning the public API

---

## Project Structure

```text
neura_rag_chatbot/
│
├── app/
│   │
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py
│   │
│   ├── conversations/
│   │   ├── __init__.py
│   │   └── store.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   └── retriever.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   │
│   └── services/
│       ├── __init__.py
│       └── gemini_service.py
│
├── scripts/
│   └── test_gemini.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Environment Variables

The project uses environment variables for configuration.

Create a `.env` file in the project root.

Example:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here

APP_ENV=development
GEMINI_MODEL=gemini-3.6-flash

RAG_ENABLED=false

MAX_HISTORY_MESSAGES=12
CONVERSATION_TTL_MINUTES=30
```

Only `GEMINI_API_KEY` is required at the moment because the other settings have default values in the application configuration.

### Important

Never commit the real `.env` file.

The following file is safe to commit:

```text
.env.example
```

The following file must remain private:

```text
.env
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd neura_rag_chatbot
```

---

### 2. Create a Python virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

After activation, the terminal should look similar to:

```text
(.venv) user@machine:~/neura_rag_chatbot$
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Current main dependencies include:

```text
FastAPI
Google GenAI SDK
python-dotenv
Pydantic Settings
```

---

### 4. Create the environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit:

```text
.env
```

and add a valid Gemini API key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## Running the Application

Start the development server with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available locally at:

```text
http://localhost:8000
```

---

## GitHub Codespaces

The project can be developed and tested completely inside GitHub Codespaces.

Start the application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

GitHub Codespaces should automatically detect port:

```text
8000
```

and provide a forwarded browser URL.

The forwarded URL can be used to test the chatbot without installing the project locally.

For internal demonstrations, the Codespaces forwarded port can also be shared if its visibility settings allow access.

Codespaces should be treated as a development and demonstration environment, not permanent production hosting.

---

## API Documentation

FastAPI automatically generates interactive Swagger documentation.

Open:

```text
http://localhost:8000/docs
```

When using Codespaces, use the forwarded Codespaces URL followed by:

```text
/docs
```

Example:

```text
https://your-codespace-url.app.github.dev/docs
```

---

# API Endpoints

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "Neura RAG Chatbot"
}
```

This endpoint can be used for:

- service monitoring
- deployment health checks
- uptime checks
- infrastructure readiness checks

---

## Chat

```http
POST /api/v1/chat
```

### Start a New Conversation

Request:

```json
{
  "message": "What is an ERP system?",
  "conversation_id": null
}
```

Example response:

```json
{
  "success": true,
  "conversation_id": "56413f91-ff5f-40bd-a016-9eec83b79f61",
  "message": "An Enterprise Resource Planning system is...",
  "mode": "general"
}
```

The generated `conversation_id` should be stored by the frontend.

---

## Continue an Existing Conversation

Send the same `conversation_id` with the next message.

Example:

```json
{
  "message": "Does it normally include inventory management?",
  "conversation_id": "56413f91-ff5f-40bd-a016-9eec83b79f61"
}
```

The chatbot receives previous conversation history and can understand that the word:

```text
it
```

refers to the ERP system discussed previously.

Example response:

```json
{
  "success": true,
  "conversation_id": "56413f91-ff5f-40bd-a016-9eec83b79f61",
  "message": "Yes. Inventory management is commonly included as an ERP module...",
  "mode": "general"
}
```

---

## Invalid Conversation

If a conversation ID does not exist or has expired:

```json
{
  "message": "Hello",
  "conversation_id": "invalid-id"
}
```

the API returns:

```json
{
  "detail": "Conversation not found."
}
```

with HTTP status:

```text
404
```

---

## AI Service Failure

If Gemini or another internal AI component fails, the public API returns a safe response:

```json
{
  "detail": "The AI service is temporarily unavailable."
}
```

with HTTP status:

```text
503
```

Internal exceptions are logged on the server rather than exposed directly to website visitors.

---

# Conversation Management

The current conversation implementation stores messages in application memory.

A conversation contains:

```text
Conversation ID
      |
      v
User Message
      |
      v
Assistant Response
      |
      v
User Message
      |
      v
Assistant Response
```

---

## Conversation History Limit

Default:

```text
12 messages
```

This is controlled by:

```env
MAX_HISTORY_MESSAGES=12
```

When the limit is exceeded, the oldest messages are removed.

For example:

```text
Messages 1 to 20 received

Stored:
Messages 9 to 20
```

This helps control:

- Gemini token usage
- response latency
- API cost
- memory consumption
- excessively large prompts

---

## Conversation Expiration

Default inactivity timeout:

```text
30 minutes
```

Controlled by:

```env
CONVERSATION_TTL_MINUTES=30
```

If the conversation is inactive beyond the configured timeout, it expires.

A future request using that old conversation ID will return:

```text
404 Conversation not found
```

---

## Current Conversation Storage Limitation

Conversation history is currently stored in Python application memory.

Therefore:

```text
Server restart
      |
      v
Stored conversations are lost
```

This implementation is appropriate for:

- development
- testing
- demonstrations
- early-stage MVP development

Before production deployment, conversation storage should be replaced with persistent or distributed storage.

Possible options include:

```text
Redis
PostgreSQL
Supabase
managed database
```

The architecture should allow the in-memory store to be replaced later without changing the public `/api/v1/chat` interface.

---

# Neura AI Guardrails

The chatbot currently does not contain a verified Neura Solutions knowledge base.

Therefore, the system prompt instructs Gemini not to invent company-specific information.

The chatbot should not fabricate information about:

- Neura Solutions pricing
- NeuraERP pricing
- clients
- customers
- case studies
- company policies
- product capabilities
- internal processes
- partnerships
- confidential information

For example:

```text
User:
How much does NeuraERP cost?
```

Expected behavior:

```text
The assistant should state that it does not have verified pricing information
and should direct the visitor to the Neura Solutions team for an accurate quote.
```

It should not invent a price.

---

# RAG Architecture

RAG stands for:

```text
Retrieval-Augmented Generation
```

The application already includes a knowledge retrieval abstraction even though a real knowledge base has not yet been connected.

Current behavior:

```text
Question
   |
   v
NullKnowledgeRetriever
   |
   v
No context
   |
   v
Gemini
```

Future behavior:

```text
Question
   |
   v
Embedding
   |
   v
Vector Search
   |
   v
Neura Knowledge Base
   |
   v
Relevant Documents
   |
   v
Context
   |
   v
Gemini
   |
   v
Grounded Answer
```

---

## RAG Modes

When no knowledge context is used:

```json
{
  "mode": "general"
}
```

Later, when verified knowledge-base information is retrieved:

```json
{
  "mode": "rag"
}
```

This allows the frontend and backend to know whether an answer was generated using retrieved company knowledge.

---

## Future Knowledge Sources

Potential Neura knowledge sources include:

- Neura Solutions website
- NeuraERP documentation
- product documentation
- service documentation
- company profile
- approved pricing documents
- FAQs
- technical documentation
- support documentation
- company policies
- approved case studies
- internal product information intended for public use

---

# CORS

The API currently restricts browser cross-origin access to approved frontend origins.

Example allowed frontend:

```text
https://neura-solutions.vercel.app
```

The application does not intentionally use:

```text
*
```

as the production CORS policy.

This helps prevent arbitrary websites from directly calling the browser-facing API.

Additional production domains can be added later through configuration.

---

# Testing Gemini Directly

A basic Gemini connectivity test is available at:

```text
scripts/test_gemini.py
```

Run:

```bash
python scripts/test_gemini.py
```

This can be used to confirm:

```text
Python
  |
  v
Gemini API
  |
  v
Successful response
```

before debugging the FastAPI layer.

---

# Development Workflow

Recommended Git workflow:

```text
Owner Repository
      |
      v
Developer Fork
      |
      v
Feature Branch
      |
      v
Development
      |
      v
Testing
      |
      v
Commit
      |
      v
Push
      |
      v
Pull Request
```

Example feature branch:

```text
feat/initial-chatbot
```

Avoid developing directly on:

```text
main
```

---

# Git Security

Never commit:

```text
.env
API keys
passwords
access tokens
customer data
private credentials
production secrets
```

The `.gitignore` should protect files such as:

```text
.env
.env.*
.venv/
__pycache__/
```

while allowing:

```text
.env.example
```

to remain in the repository.

---

# Current Development Status

The following components are currently implemented:

```text
[x] Python project setup
[x] FastAPI application
[x] Health endpoint
[x] Gemini API connection
[x] Chat endpoint
[x] Neura system prompt
[x] General AI assistance
[x] Multi-turn conversations
[x] Conversation IDs
[x] Invalid conversation handling
[x] History trimming
[x] Conversation expiration
[x] Central configuration
[x] Environment variables
[x] Secure API key handling
[x] CORS configuration
[x] Safe public error responses
[x] Server-side error logging
[x] Optional RAG abstraction
[x] RAG disabled mode
[ ] Real Neura knowledge base
[ ] Embeddings
[ ] Vector database
[ ] RAG source citations
[ ] Persistent conversation storage
[ ] Production rate limiting
[ ] Automated test suite
[ ] Monitoring
[ ] Production deployment
[ ] Website chatbot frontend integration
```

---

# Production Roadmap

Before connecting the service to the public Neura Solutions website, planned work includes:

## Phase 1: Core Chatbot

- FastAPI
- Gemini integration
- system instructions
- conversation support
- API validation

Status:

```text
Mostly complete
```

---

## Phase 2: Production API Hardening

Planned:

- rate limiting
- request IDs
- structured logging
- improved exception handling
- input sanitization review
- abuse protection
- API usage monitoring
- automated tests
- production configuration separation

---

## Phase 3: Persistent Conversations

Replace the current in-memory conversation store with:

```text
Redis
or
Database-backed storage
```

This will allow conversations to survive:

- server restarts
- multiple API instances
- horizontal scaling

---

## Phase 4: RAG Knowledge Base

Planned components:

```text
Document Loader
      |
      v
Text Cleaning
      |
      v
Chunking
      |
      v
Embeddings
      |
      v
Vector Database
      |
      v
Retriever
      |
      v
Relevant Context
      |
      v
Gemini
```

---

## Phase 5: Source Grounding

RAG responses should eventually include source information.

Example:

```json
{
  "success": true,
  "conversation_id": "uuid",
  "message": "NeuraERP supports...",
  "mode": "rag",
  "sources": [
    {
      "title": "NeuraERP Product Documentation",
      "reference": "..."
    }
  ]
}
```

---

## Phase 6: Website Integration

The Neura website frontend will call:

```http
POST /api/v1/chat
```

The frontend will be responsible for:

- chat interface
- message display
- Markdown rendering
- storing the active conversation ID
- loading indicators
- error messages
- responsive design
- accessibility
- retry behavior

---

## Phase 7: Production Deployment

The API can later be deployed to a production hosting environment such as:

```text
Google Cloud Run
Railway
AWS
Azure
or another Docker-compatible platform
```

GitHub Codespaces should remain primarily a development environment.

---

# Example Final Production Flow

```text
Neura Website Visitor
        |
        v
Chat Widget
        |
        v
Neura AI API
        |
        +----------------------+
        |                      |
        v                      v
Conversation Store       RAG Retriever
                               |
                               v
                       Neura Knowledge Base
                               |
        +----------------------+
        |
        v
Gemini
        |
        v
Guarded Response
        |
        v
Source Information
        |
        v
Website Chat UI
```

---

# Important Note

The current chatbot is an AI system built for Neura Solutions Limited using Gemini as the underlying foundation model.

Gemini itself is not a model trained by Neura Solutions Limited.

The Neura-specific system consists of the surrounding application architecture, including:

- chatbot logic
- conversation management
- prompts
- guardrails
- API architecture
- future retrieval system
- future knowledge base
- business rules
- website integration

---

# Company

**Neura Solutions Limited**

AI chatbot microservice for the Neura Solutions website.