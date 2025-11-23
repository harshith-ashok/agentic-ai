# Agentic MCP - FAISS Memory (simple)

1. create `virtualenv`:

`python -m venv .venv`

`source .venv/bin/activate`

2. install:
   `pip install -r requirements.txt`

3. run:
   `uvicorn app.main:app --reload --port 8000`

# Example curl commands

## Add a message

```bash
curl -X POST "http://127.0.0.1:8000/add_message" -H "Content-Type: application/json" -d '{
"message_id": "msg-1",
"conversation_id": "conv-1",
"role": "user",
"content": "I was working on the FAISS memory system today",
"timestamp": "2025-11-23T07:00:38.834823",
"tags": ["faiss", "memory", "work"]
}'
```

## Add another message

```bash
curl -X POST "http://127.0.0.1:8000/add_message" -H "Content-Type: application/json" -d '{
"message_id": "msg-2",
"conversation_id": "conv-1",
"role": "assistant",
"content": "Ok, I can help you continue that project.",
"timestamp": "2025-11-23T07:01:00",
"tags": ["faiss","assistant"]
}'
```

## Search by text

```bash
curl -X POST "http://127.0.0.1:8000/search" -H "Content-Type: application/json" -d '{
"query":"faiss memory system",
"k":5
}'
```

## Search by tag

```bash
curl -X POST "http://127.0.0.1:8000/search_by_tag" -H "Content-Type: application/json" -d '{
"tag":"faiss",
"limit":20
}'
```

## Get exact message

```bash
curl "http://127.0.0.1:8000/message/msg-1"
```
