from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
#from anthropic import Anthropic
from dotenv import load_dotenv
import json, sqlite3, datetime, os

load_dotenv()

app = FastAPI()
#client = Anthropic()

def load_kb():
    with open("kb.json", "r") as f:
        return json.load(f)["entries"]

def search_kb(query: str):
    # Skip KB for negation queries
    negation_words = {"not", "never", "don't", "doesnt", "doesn't", "isn't",
                      "isnt", "aren't", "arent", "no", "without", "except", "exclude"}
    query_lower = query.lower()
    query_words = set(query_lower.split())

    if query_words & negation_words:
        return None

    # Remove common filler words that cause false matches
    stop_words = {"what", "is", "a", "an", "the", "how", "do", "i", "my",
                  "can", "will", "are", "does", "me", "to", "for", "of",
                  "in", "it", "this", "that", "and", "or", "about"}
    meaningful_words = query_words - stop_words

    # Need at least one meaningful word to match
    if not meaningful_words:
        return None

    best_match = None
    best_score = 0
    for entry in load_kb():
        text = (entry["question"] + " " + " ".join(entry["tags"])).lower()
        score = sum(1 for word in meaningful_words if word in text)
        if score > best_score:
            best_score = score
            best_match = entry

    # Require at least 2 meaningful words to match, or 1 if query is short
    min_score = 2 if len(meaningful_words) >= 3 else 1
    return best_match if best_score >= min_score else None

def init_db():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_query TEXT,
            status TEXT DEFAULT 'open',
            resolution TEXT,
            created_at TEXT,
            resolved_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def create_ticket(query: str):
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute(
        "INSERT INTO tickets (customer_query, status, created_at) VALUES (?, ?, ?)",
        (query, "open", now)
    )
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def resolve_ticket(ticket_id: int, resolution: str):
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute(
        "UPDATE tickets SET status=?, resolution=?, resolved_at=? WHERE id=?",
        ("resolved", resolution, now, ticket_id)
    )
    conn.commit()
    conn.close()

def get_all_tickets():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "query": r[1],
            "status": r[2],
            "resolution": r[3],
            "created_at": r[4],
            "resolved_at": r[5]
        }
        for r in rows
    ]

def add_to_kb(question: str, answer: str):
    with open("kb.json", "r") as f:
        data = json.load(f)
    new_id = max(e["id"] for e in data["entries"]) + 1
    data["entries"].append({
        "id": new_id,
        "question": question,
        "answer": answer,
        "tags": question.lower().split()[:4]
    })
    with open("kb.json", "w") as f:
        json.dump(data, f, indent=2)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    history = body.get("history", [])

    kb_match = search_kb(user_message)
    if kb_match:
        return JSONResponse({
            "response": kb_match["answer"],
            "source": "Knowledge Base"
        })

    return JSONResponse({
        "source": "AI_NEEDED"
    })
     
@app.post("/ticket")
async def raise_ticket(request: Request):
    body = await request.json()
    query = body.get("query", "")
    ticket_id = create_ticket(query) 
    return JSONResponse({
        "message": f"Ticket #{ticket_id} created successfully. Our team will get back to you within 24 hours.",
        "ticket_id": ticket_id
    })

@app.get("/tickets")
async def list_tickets():
    return JSONResponse(get_all_tickets())

@app.post("/tickets/{ticket_id}/resolve")
async def resolve(ticket_id: int, request: Request):
    body = await request.json()
    resolution = body.get("resolution", "")
    resolve_ticket(ticket_id, resolution)

    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("SELECT customer_query FROM tickets WHERE id=?", (ticket_id,))
    row = c.fetchone()
    conn.close()
    if row:
        add_to_kb(row[0], resolution)

    return JSONResponse({
        "message": f"Ticket #{ticket_id} resolved and answer added to Knowledge Base."
    })

app.mount("/static", StaticFiles(directory="static"), name="static")