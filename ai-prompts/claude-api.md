## 🧠 Claude Prompt — Dynamic FastAPI Backend for Agentic Assistant

```
You are helping me build a **FastAPI backend** for my “Agentic Personal Everyday Assistant.”  
All backend code must live in the `/api` folder.  
The assistant stores data in Markdown files under `/templates/`.  
There is only one user — no authentication required.

---

## 📁 Existing Folder Structure

.
├── api
└── templates
    ├── avatars
    │   ├── archives/
    │   ├── bio.md
    │   └── personality.md
    ├── events/
    ├── event.md
    ├── people.md
    ├── tags.md
    ├── prompt.md

---

## 🧩 Required System Behavior

You are to build a **dynamic, schema-flexible FastAPI API** that provides CRUD endpoints for all the assistant’s knowledge components:

- ✅ Events (weekly, time-based entries)
- ✅ Tags (stored in tags.md)
- ✅ People (with dynamic categories)
- ✅ Avatars (bio/personality)
- ✅ AI endpoint (Llama 3.2 placeholder)

No database — only Markdown + JSON hybrid persistence in `/templates/`.

---

## 🏗️ Folder Structure (to create under `/api`)

```

/api/
├── main.py
├── routers/
│   ├── events.py
│   ├── people.py
│   ├── tags.py
│   ├── avatars.py
│   └── ai.py
├── models/
│   ├── event.py
│   ├── person.py
│   ├── tag.py
│   ├── avatar.py
├── utils/
│   ├── file_ops.py        # read/write Markdown safely
│   ├── week_utils.py      # extract year/month/week from date
│   ├── md_parser.py       # parse Markdown headers, lists
│   └── cache.py           # lightweight in-memory cache for tags/categories
└── **init**.py

````

Each router should have routes with proper prefixes (`/events`, `/tags`, `/people`, `/avatars`, `/ai`).

---

## 🧱 Entities & Endpoints

### 1. **Events**
- Fields:
  - `id` (UUID)
  - `title` (str)
  - `date` (datetime)
  - `tags` (list[str])
  - `topics` (list[str])
  - `backlinks` (list[str])
  - `weather` (str)
  - `location` (str)
  - `time_of_entry` (datetime)
  - `mood` (str)
  - `content` (str)
- Stored under `/templates/events/{year}/{month}/{week}.md`
- Routes:
  - `POST /events/` → create event
  - `GET /events/{id}` → read
  - `PUT /events/{id}` → update
  - `DELETE /events/{id}` → delete
  - `GET /events/week/{year}/{month}/{week}` → list events in that week

---

### 2. **Tags** (Dynamic)
- Source: `/templates/tags.md`
- Each tag:
  - `id` (UUID)
  - `name` (slug, ≤3 words)
  - `description` (string)
  - `related_tags` (list[str])
- Routes:
  - `GET /tags/` → list all tags (read directly from tags.md)
  - `POST /tags/` → add new tag (auto-appends to tags.md)
  - `PUT /tags/{id}` → update description/relations
  - `DELETE /tags/{id}` → remove tag and rewrite file
- The system dynamically rebuilds its tag list when any change occurs.

---

### 3. **People** (Dynamic Categories)
- Source: `/templates/people.md`
- Fields:
  - `id` (UUID)
  - `name` (str)
  - `category` (one of the categories listed under “## Categories” in people.md)
  - `description` (str)
  - `first_mentioned` (datetime)
  - `last_mentioned` (datetime)
- Routes:
  - `GET /people/` → list all
  - `POST /people/` → create new person
  - `PUT /people/{id}` → update person
  - `DELETE /people/{id}` → delete
  - `GET /people/categories` → get all categories
  - `POST /people/categories` → add a new category (updates the markdown “## Categories” section)
- The category list auto-refreshes from the file; no manual enums.

---

### 4. **Avatars**
- Stored under `/templates/avatars/`
  - `bio.md` → static info
  - `personality.md` → active phase
  - `archives/phase_x.md` → previous versions
- Routes:
  - `GET /avatars/personality`
  - `PUT /avatars/personality` (archive old and replace)
  - `GET /avatars/bio`
  - `PUT /avatars/bio`

---

### 5. **AI Integration (Llama 3.2)**
Add `/ai/query` endpoint:
```python
@router.post("/query")
def query_llm(prompt: str):
    """
    Placeholder Llama 3.2 integration.
    Later this will embed and retrieve context from templates.
    """
    return {"response": "stub for Llama 3.2"}
````

---

## ⚙️ Technical Specs

* Framework: **FastAPI**
* Python: 3.10+
* Swagger & ReDoc enabled
* Pydantic models for validation
* Markdown parsing via custom utility functions
* All CRUD operations update Markdown directly
* Dynamic cache for tags & categories (reloads on write)
* Return JSON responses with proper status codes
* Code well-documented for Swagger auto-generation

---

## 🧩 Output Requirements

Please generate:

1. Full folder + file structure under `/api/`
2. Working example code for each router and model
3. Example utils (`md_parser.py`, `file_ops.py`, `week_utils.py`, `cache.py`)
4. A small `README.md` in `/api/` explaining how to run:

   ```
   uvicorn api.main:app --reload
   ```
5. Ensure dynamic behavior:

   * New tags/categories can be added via API
   * Markdown updates reflect immediately on GET requests

---

## 🚀 Future Hooks

Leave placeholders for:

* integrating vector memory retrieval
* connecting to a JS frontend
* syncing with local Llama 3.2 via Ollama API later

---

Use clean, modular, production-grade code — this API will be the backend of my evolving personal agent.

