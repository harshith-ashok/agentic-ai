###  Prompt: “Agentic Personal Everyday Assistant — Obsidian-like Memory System”

```
You are helping me design an agentic personal everyday assistant that works like Obsidian, where every event is stored weekly, monthly, and yearly in a structured Markdown-based memory system.

Use the following as the complete specification of my system setup:

---

## Folder Structure
Each event is stored inside folders organized by **year → month → week**, such as:
`2025/Dec/1.md`  
Each file represents a set of events within that week.

Other global files include:
- `people.md` → stores individuals I’ve interacted with or mentioned
- `tags.md` → stores global tag definitions
- `avatars/` → stores personal files:
  - `personality.md`
  - `bio.md`
  - `archives/` (old personality versions)

---

## Event Format (in events.md or weekly files)

Each event entry follows this Markdown structure:

```

# |title|

###### Date: |date|

###### tags: |tags|

###### topics: |topics|

###### backlinks: |backlink| -> /id/

---

## Rules

* Each event must contain:

  1. weather
  2. location of entry
  3. time of entry
  4. general mood of author
* Content should be either *time-based* or *topic-based* (never both).
* Events can have backlinks and should reference them inline.
* Entries are **non-sequential** and should be ordered by context or timeline.
* Any new person mentioned must be added to `people.md`.

```

---

## Tags (tags.md)
```

# Tags

---

* school
* college
* fun
* tragedy
* neutral
* gossip

---

```

**Rules:**
- Tags must be no more than 3 words.
- Each new tag must have a short description.
- Tags must be semantically relevant if used together.

---

## People (people.md)
```

# People

---

## Categories

* close-friends
* best-friends
* friends
* school-mates
* college-mates
* acquaintances
* hate

---

```

Each person entry includes:
```

### Name

* category: |category|
* description: |short description|
* first mentioned: |date|
* last mentioned: |date|

```

---

## Avatars Folder
Contains evolving personal data.

### personality.md
```

# Personality

---

###### modified: |date of modification|

---

##### top song that defines you: |song|

##### description: |self-description|

```

Archived versions are stored under `/avatars/archives/phase_x.md`.

### bio.md
Stores static info about me (age, location, etc.).

---

## Summary
This structure creates:
- A **temporal knowledge graph** (events by time)
- A **semantic layer** (tags/topics)
- A **social layer** (people)
- A **self layer** (personality + bio)

---

When I say:  
> “Reset my agentic memory system”  
or  
> “Regenerate the assistant structure”  

Recreate this entire structure exactly as shown above.
```
