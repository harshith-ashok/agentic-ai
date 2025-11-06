from fastapi import FastAPI
from routers import events, people, tags, avatars, ai

app = FastAPI(
    title="Agentic Personal Everyday Assistant API",
    description="Backend for managing the assistant's knowledge components.",
    version="0.1"
)

# Include routers
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(people.router, prefix="/people", tags=["People"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(avatars.router, prefix="/avatars", tags=["Avatars"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
