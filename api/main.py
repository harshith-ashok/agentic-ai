# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import events, tags, people, avatars, ai

app = FastAPI(
    title="Agentic Assistant Backend",
    description="FastAPI backend storing data in Markdown files under /templates/",
    version="0.1.0",
)

# Allow CORS for local frontend usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(avatars.router, prefix="/avatars", tags=["avatars"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Agentic Assistant API - Markdown-backed"}
