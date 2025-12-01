from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, PlainTextResponse, JSONResponse
import json
import asyncio
import httpx
import redis
from pymongo import MongoClient
from memory_manager import MemoryManager

app = FastAPI()

REDIS_URL = "redis://localhost:6379"
MONGO_URL = "mongodb://localhost:27017"

memory = MemoryManager(REDIS_URL, MONGO_URL)


async def ollama_generate(prompt):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False}
        )
        return r.json()["response"]


async def ollama_stream(prompt):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": True}
        ) as r:
            async for line in r.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    user_message = body["message"]

    memory.save_short(session_id, user_message)
    memory.save_long(user_message)

    short_context = memory.get_short(session_id)[-5:]
    long_context = memory.get_long(user_message, top_k=3)

    context_block = ""
    if short_context:
        context_block += "\n".join(short_context) + "\n"
    if long_context:
        context_block += "\n".join(long_context) + "\n"

    final_prompt = context_block + "User: " + user_message + "\nAssistant:"

    response = await ollama_generate(final_prompt)

    memory.save_short(session_id, response)

    return {"response": response}


@app.post("/chat-stream")
async def chat_stream(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    user_message = body["message"]

    memory.save_short(session_id, user_message)
    memory.save_long(user_message)

    short_context = memory.get_short(session_id)[-5:]
    long_context = memory.get_long(user_message, top_k=3)

    context_block = ""
    if short_context:
        context_block += "\n".join(short_context) + "\n"
    if long_context:
        context_block += "\n".join(long_context) + "\n"

    final_prompt = context_block + "User: " + user_message + "\nAssistant:"

    async def event_stream():
        async for chunk in ollama_stream(final_prompt):
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/reset-short")
async def reset_short(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    memory.clear_short(session_id)
    return {"status": "short term memory cleared"}


@app.post("/reset-long")
async def reset_long():
    memory.clear_long()
    return {"status": "long term memory cleared"}


@app.post("/hard-reset")
async def hard_reset():
    r = redis.Redis.from_url(REDIS_URL)
    r.flushall()

    mongo = MongoClient(MONGO_URL)
    mongo.drop_database("ai_memory")

    memory.index.reset()

    return {"status": "ALL MEMORY CLEARED"}


@app.get("/health")
async def health():
    redis_ok = "OK"
    mongo_ok = "OK"
    ollama_ok = "OK"

    try:
        redis.Redis.from_url(REDIS_URL).ping()
    except:
        redis_ok = "FAIL"

    try:
        MongoClient(MONGO_URL).admin.command("ping")
    except:
        mongo_ok = "FAIL"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:11434/api/tags")
            if r.status_code != 200:
                ollama_ok = "FAIL"
    except:
        ollama_ok = "FAIL"

    text = f"redis={redis_ok}\nmongodb={mongo_ok}\nollama={ollama_ok}"
    return PlainTextResponse(text)
