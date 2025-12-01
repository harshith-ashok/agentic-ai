# Memory Enabled AI PLug-in

A FastAPI-based conversational AI system with dual-layer memory management (short-term and long-term) powered by Ollama LLMs. This project integrates Redis for session-based short-term memory, MongoDB for persistent long-term memory, and FAISS for semantic similarity search.

## Overview

This system enables intelligent conversations with memory capabilities:

- Short-term memory using Redis for session-specific conversation history
- Long-term memory using MongoDB with semantic embeddings stored in FAISS
- Integration with Ollama models (default: llama3.2) for generating responses
- Real-time streaming responses for enhanced user experience

## Features

- Chat endpoint with context-aware responses
- Streaming chat endpoint for real-time response delivery
- Dual memory system with independent management
- Session-based conversation tracking
- Memory reset capabilities (short-term, long-term, or complete)
- Health check endpoint for service status
- Context augmentation using semantic similarity search

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Ollama with llama3.2 model installed locally

## Installation

Clone the repository and install dependencies:

```bash
pip install -r req.txt
```

## Configuration

The system uses the following default connections:

- Redis: localhost:6379
- MongoDB: localhost:27017
- Ollama: localhost:11434

These can be modified by updating the REDIS_URL and MONGO_URL variables in main.py.

## Setup

Start the required services using Docker Compose:

```bash
docker-compose up -d
```

This will start MongoDB and Redis containers. Ensure Ollama is running separately.

Run the FastAPI application:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

## API Endpoints

POST /chat

- Request body: { "session_id": "string", "message": "string" }
- Returns a complete response with context consideration
- Saves both user message and AI response to memory

POST /chat-stream

- Request body: { "session_id": "string", "message": "string" }
- Returns response as Server-Sent Events stream
- Allows real-time display of generated text

POST /reset-short

- Request body: { "session_id": "string" }
- Clears short-term memory for a specific session

POST /reset-long

- Clears all long-term memory

POST /hard-reset

- Completely clears Redis, MongoDB, and FAISS indices
- Use with caution

GET /health

- Returns status of Redis, MongoDB, and Ollama services
- Output format: service=OK/FAIL on separate lines

## System Architecture

Memory Manager

- Manages dual memory layers with semantic embeddings
- Uses SentenceTransformer (all-MiniLM-L6-v2) for embedding generation
- Stores embeddings in FAISS for efficient similarity search
- Implements UUID-based tracking for all stored items

Message Flow

1. User message received and stored in short-term memory
2. Message text also stored in long-term memory with embedding
3. Short-term context (last 5 messages) retrieved
4. Long-term context retrieved using semantic similarity (top 3)
5. Context blocks combined into final prompt for LLM
6. Response generated and stored in memory

## Dependencies

- fastapi: Web framework for building APIs
- uvicorn: ASGI server
- pymongo: MongoDB driver
- redis: Redis client
- faiss-cpu: Vector similarity search
- sentence-transformers: Text embedding generation
- requests: HTTP library
- python-dotenv: Environment variable management
- httpx: Async HTTP client

## Development

The project uses async/await for non-blocking I/O operations. All LLM requests timeout is set to None to allow longer processing times.

## Troubleshooting

If the health check shows services failing:

- Verify Docker containers are running: docker ps
- Check Ollama is installed and running locally
- Confirm port availability (6379 for Redis, 27017 for MongoDB, 11434 for Ollama)
- Review logs in docker-compose.yml for persistent services
