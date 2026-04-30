# 🏥 HealthAssist — AI-Powered Customer Support System

An end-to-end intelligent customer support platform for a health insurance company, built using the Claude API (Anthropic). The system deflects common queries via a knowledge base, falls back to AI for unknown queries, and escalates to ticketed support when needed.

---

## 🎯 Problem Statement

Health insurance companies handle thousands of repetitive customer queries daily. Human agents answering these is expensive and slow. This system automates query resolution through a three-layer deflection architecture — only escalating to humans when truly necessary.

---

## 🏗️ Architecture

    User Query
        │
        ▼
    ┌─────────────────────┐
    │   Knowledge Base    │  ← Keyword search on JSON entries
    │   (kb.json)         │  ← Returns answer if match found
    └─────────┬───────────┘
              │ No match
              ▼
    ┌─────────────────────┐
    │   Claude AI         │  ← Guardrailed to health insurance domain
    │   (Haiku model)     │  ← Maintains conversation history
    └─────────┬───────────┘
              │ User still unsatisfied
              ▼
    ┌─────────────────────┐
    │   Ticket System     │  ← SQLite-backed support tickets
    │   (SQLite DB)       │  ← Agent resolves → feeds back to KB
    └─────────────────────┘

---

## ✨ Features

- **Chat Interface** — Clean conversational UI with typing indicators and source badges
- **Knowledge Base Q&A** — Instant answers for known queries (free, fast)
- **AI Fallback** — Claude Haiku handles unknown queries with domain guardrails
- **Source Transparency** — Every response labelled "Knowledge Base" or "AI Assistant"
- **Ticket Creation** — One-click escalation to human support
- **Ticket Resolution** — Agent dashboard to view and resolve open tickets
- **KB Feedback Loop** ⭐ — Resolved tickets automatically added back to KB

---

## 🛠️ Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| LLM | Claude Haiku via Puter.js | Free, no API key needed, user-pays model |
| Backend | FastAPI (Python) | Async, modern, auto-docs |
| Knowledge Base | JSON file | Simple, fast, swappable |
| Ticket Store | SQLite | Zero-config, built into Python |
| Frontend | Vanilla HTML/CSS/JS | No build tools, fully portable |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- A free Puter account (sign up at https://puter.com) — needed for AI responses

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/my-health-support-ai.git
cd health-support-ai
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
uvicorn main:app --reload
```

**5. Open in browser**
http://127.0.0.1:8000

---

## 📁 Project Structure
health-support/
├── main.py           ← FastAPI backend, all route handlers
├── kb.json           ← Knowledge base entries
├── requirements.txt  ← Python dependencies
├── .env              ← API key (not committed to Git)
└── static/
└── index.html    ← Chat UI and ticket dashboard

---

## 🔄 How the KB Feedback Loop Works

1. Customer raises a ticket with an unresolved query
2. Agent opens the Tickets panel and types a resolution
3. On clicking Resolve:
   - Ticket status → `resolved` in SQLite
   - Resolution automatically appended to `kb.json` as a new entry
4. Next time a similar query comes in → KB matches it directly, no AI call needed

---

## ⚠️ Known Limitations & Production Considerations

| Current Approach | Production Alternative |
|---|---|
| Keyword matching for KB search | Semantic search with vector embeddings (Vertex AI Matching Engine / Pinecone) |
| JSON file for KB | Vector database or Cloud Firestore |
| SQLite for tickets | PostgreSQL + webhook integration with Zendesk/ServiceNow |
| No authentication | OAuth2 / JWT for agent dashboard |
| No rate limiting | API gateway with rate limiting |
| Manual KB review | Human-in-the-loop review before KB entries go live |

---