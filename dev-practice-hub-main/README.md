# AI Job Application Tracker

An agentic Python system that monitors Gmail, classifies job-application
emails with an LLM, stores them in SQLite, indexes them in a RAG vector
store for semantic Q&A, and optionally mirrors them to Google Sheets.
A Streamlit dashboard visualizes the results.

## Architecture

This used to be two separate, conflicting pipelines (a Google-Sheets
script and a broken SQLite one). It's now one pipeline with SQLite as
the single source of truth:

```
Gmail API → EmailAgent (filter + dedup) → ClassifierAgent (LLM)
          → SQLite (source of truth) → RAGMemory (ChromaDB, for Q&A)
                                      → sheets_sync.py (optional mirror)
```

- **`main.py`** — the pipeline above, run on a schedule via GitHub Actions.
- **`dashboard.py`** — Streamlit UI reading from SQLite.
- **`sheets_sync.py`** — optional, one-way SQLite → Google Sheets export.
- **`rag_memory.py`** — semantic Q&A over stored applications.

## Setup

1. **Clone and install**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Fill in `.env`** with your own OpenAI API key. `.env` is gitignored
   — never commit it.

3. **Gmail OAuth (local, one-time)**
   - In Google Cloud Console, create OAuth 2.0 credentials (Desktop app)
     and download them as `credentials.json` into the project root.
   - `credentials.json` and the `token.json` it generates are both
     gitignored — never commit them.
   - Run `python main.py` once locally; it will open a browser to
     authenticate and save `token.json`.

4. **Initialize the database**
   ```bash
   python setup_database.py
   ```

5. **Run it**
   ```bash
   python main.py          # fetch + classify + store
   streamlit run dashboard.py   # view results
   ```

### Optional: Google Sheets export

Set `SHEET_ID` in `.env`, create a Google service account with edit
access to that sheet, save its key as `service_account.json`
(gitignored), then run:
```bash
python sheets_sync.py
```

### CI setup (GitHub Actions)

GitHub Actions can't do an interactive OAuth flow, so generate
`token.json` locally first (step 3 above), then add these as
**repository secrets** (Settings → Secrets and variables → Actions) —
never as files in the repo:

- `OPENAI_API_KEY`
- `GMAIL_TOKEN_B64` — `base64 -w0 token.json` output
- `SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_B64` (optional, for Sheets sync)

## Tech Stack

- Python, OpenAI API (gpt-4o-mini), ChromaDB
- Gmail API, Google Sheets API (optional), OAuth2
- SQLite, Streamlit + Plotly
- GitHub Actions (scheduled, no server needed)

## Features

- Auto-classify email status (Applied / Interview / Assessment / Offer / Rejected)
- LLM-based company and role extraction
- Duplicate detection keyed on Gmail message ID (safe to re-run)
- RAG-powered semantic Q&A over your job history
- Streamlit dashboard with filters and charts
- Scheduled via GitHub Actions every 15 minutes

## Testing

Each `test_*.py` runs standalone (`python test_database.py`) or via
`pytest`, using mocks/temp databases — no live API keys or Gmail auth
required:
```bash
python test_classifier.py
python test_database.py
python test_duplicate.py
python test_gmail.py
python test_read_database.py
```

## Roadmap (not implemented yet)

- `agents/planner_agent.py` — suggest follow-up actions based on
  application age and status.
- `agents/resume_match_agent.py` — score a resume against a job
  description pulled from a tracked email.

Both currently exist as documented stubs that raise `NotImplementedError`.

## Security notes

- Never commit `.env`, `credentials.json`, `token.json`, or
  `service_account.json` — all are in `.gitignore`.
- If you're migrating from an older version of this repo that had
  real secrets committed, **rotate them** (new OpenAI key, new OAuth
  client) — deleting the file in a new commit does not remove it from
  git history.
