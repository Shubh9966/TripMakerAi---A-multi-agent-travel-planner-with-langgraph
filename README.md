# TripMate AI — A Multi-Agent Travel Planner with LangGraph

TripMate AI plans a complete trip — flights, hotels, and a day-by-day itinerary — from a single natural-language request. A pipeline of AI agents built on **LangGraph** does the research and writing; **FastAPI** serves the app; conversation state is checkpointed in **PostgreSQL**, so a chat can be resumed with the same `thread_id`.

> Example: *"Plan a complete 7 days Japan trip from Bangladesh including flights, hotels and sightseeing under 2 lakhs."*

## How it works

Each request runs through a fixed 4-agent LangGraph pipeline:

```mermaid
flowchart LR
    START --> A[Flight Agent]
    A --> B[Hotel Agent]
    B --> C[Itinerary Agent]
    C --> D[Final Response Agent]
    D --> END
```

| Agent | Job |
|---|---|
| **Flight Agent** | Parses the request and looks up flight options via the flight search tool. |
| **Hotel Agent** | Searches for hotel/stay recommendations for the destination using Tavily. |
| **Itinerary Agent** | Calls the LLM (Groq) with the flight and hotel results to draft a day-by-day plan. |
| **Final Response Agent** | Calls the LLM again to format everything into one clean, readable travel plan. |

Every step updates a shared `TravelState` (messages, query, flight results, hotel results, itinerary, and an `llm_calls` counter), and the whole graph is checkpointed to Postgres via `PostgresSaver` — so passing the same `thread_id` back on a follow-up request continues the same conversation instead of starting over.

## Tech stack

- **Backend:** FastAPI, Uvicorn, Jinja2 (templates)
- **Agent orchestration:** LangGraph, LangChain
- **LLM:** Groq (`langchain-groq`)
- **Search tools:** Tavily (hotels), a custom flight-search tool (flights), `airportsdata` + `pycountry` for airport/city lookups
- **Persistence:** PostgreSQL, via `psycopg` + `langgraph-checkpoint-postgres`
- **Frontend:** Static HTML/CSS/JS (Jinja2-served), `marked.js` for Markdown rendering, `html2pdf.js` for PDF export
- **Deployment:** Docker (`python:3.11-slim`)

## Project structure

```
.
├── app.py                 # FastAPI app — routes, static files, templates
├── backend.py              # LangGraph graph, agents, Postgres checkpointer
├── tools/
│   ├── flight_tool.py      # Flight search tool
│   └── tavily_tool.py      # Tavily-based hotel/web search tool
├── templates/
│   └── index.html          # Main UI page (Jinja2 template)
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
├── Dockerfile
└── LICENSE
```

## API routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Renders the main UI (`templates/index.html`) |
| `POST` | `/api/travel` | Runs the agent pipeline. Body: `{ "message": "...", "thread_id": "..." }` (`thread_id` optional) |
| `GET` | `/health` | Health check for uptime/monitoring |

`POST /api/travel` returns:

```json
{
  "success": true,
  "thread_id": "user_...",
  "answer": "the final formatted travel plan",
  "flight_results": "...",
  "hotel_results": "...",
  "itinerary": "...",
  "llm_calls": 4
}
```

## Getting started

### Prerequisites

- Python 3.11+
- A PostgreSQL database (e.g. a free instance on [Render](https://render.com), [Supabase](https://supabase.com), or [Neon](https://neon.tech))
- API keys for [Groq](https://console.groq.com) and [Tavily](https://tavily.com)

### 1. Clone the repo

```bash
git clone https://github.com/Shubh9966/TripMakerAi---A-multi-agent-travel-planner-with-langgraph.git
cd TripMakerAi---A-multi-agent-travel-planner-with-langgraph
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_postgresql_connection_string
TAVILY_API_KEY=your_tavily_api_key
```

> `GROQ_API_KEY` and `DATABASE_URL` are required by `backend.py` — the app raises a clear error on startup if either is missing. `DATABASE_URL` needs `sslmode=require` for most managed Postgres providers; `backend.py` adds it automatically if it's missing from the URL. Check `tools/flight_tool.py` and `tools/tavily_tool.py` for any additional keys your flight source needs (e.g. an AviationStack key), and add them to `.env` as well.

### 4. Run it

```bash
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** in your browser. Interactive API docs are at **http://127.0.0.1:8000/docs**.

### Run with Docker instead

```bash
docker build -t tripmate-ai .
docker run -p 8000:8000 --env-file .env tripmate-ai
```

## Usage

1. Type a trip request into the input box (or pick a quick-prompt chip).
2. Click **Generate itinerary** (or press `Ctrl` + `Enter`).
3. Read the plan, **Copy** it as plain text, or **Download PDF**.
4. Send a follow-up in the same session and it continues the same thread — the app remembers the `thread_id` from the first response.

## Notes & limitations

- Flight pricing depends on the live flight source available to `flight_tool.py`; if pricing isn't available, the final response says so rather than guessing a number.
- The Postgres checkpointer keeps full conversation state per `thread_id` — clear old threads periodically if you're running this with a lot of traffic on a small database plan.

## License

MIT — see [LICENSE](LICENSE).