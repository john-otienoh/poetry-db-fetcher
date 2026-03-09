# Poetry Database Fetcher

A Python application that fetches poems from the [PoetryDB API](https://poetrydb.org/) and stores them in a PostgreSQL database. Perfect for building a personal poetry collection, data analysis, or just enjoying random poems!

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Fetch random poems** - Get random poems from the PoetryDB API
- **Search by author** - Fetch all poems by a specific poet
- **Search by title** - Find and store poems by title
- **PostgreSQL storage** - Persist poems with full text and metadata
- **JSONB support** - Store poem lines as JSON for flexibility
- **Context managers** - Clean resource management with `with` statements
- **Batch operations** - Insert multiple poems at once
- **Search functionality** - Query your local poetry database
- **Comprehensive error handling** - Graceful failure with informative messages

## Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+**
- **pip** (Python package manager)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/john-otienoh/poetry-db-fetcher.git
   cd poetry-db-fetcher
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a `.env` file** in the project root:

   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=poetry_data
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   ```

2. **Update the password** with your PostgreSQL credentials.

## Database Setup

### Option 1: Automatic Setup (Recommended)

Run the setup script to create the database and schema:

```bash
python setup_database.py
```

### Option 2: Manual Setup

1. **Create the database:**
   ```bash
   psql -U postgres -c "CREATE DATABASE poetry_data;"
   ```

2. **Run the schema:**
   ```bash
   psql -U postgres -d poetry_data -f schema.sql
   ```

### Database Schema

```sql
CREATE TABLE poems (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255) NOT NULL,
    lines JSONB DEFAULT '[]',
    linecount INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### Fetch Random Poems

```bash
python fetch_data.py
```

This will:
1. Fetch a random poem from PoetryDB
2. Store it in your local database
3. Fetch Emily Dickinson poems
4. Search for "The Raven"
5. Display database statistics

### Command Line Tools

**View all poems:**
```bash
python view_poems.py list
```

**View a specific poem:**
```bash
python view_poems.py view 1
```

**Search poems:**
```bash
python view_poems.py search "dickinson"
```

**View poems by author:**
```bash
python view_poems.py author "Emily Dickinson"
```

**Show database statistics:**
```bash
python view_poems.py stats
```

### Programmatic Usage

```python
from poetry_client import PoetryDBClient
from conn import DatabaseConnection

# Fetch and store a random poem
with PoetryDBClient() as client:
    poems = client.get_random_poem(count=1)
    
with DatabaseConnection() as db:
    db.insert_poems_batch(poems)

# Search local database
with DatabaseConnection() as db:
    results = db.search_poems("butterfly")
    for poem in results:
        print(f"{poem['title']} by {poem['author']}")
```

## Project Structure

```bash
poetry-db-fetcher/
├── config.py          # Centralised settings & logging (import from here, not basicConfig)
├── conn.py            # DatabaseConnection — all DB logic lives here
├── poetry_client.py   # PoetryDBClient — thin HTTP wrapper
├── fetch_data.py      # Entry point: fetch N random poems and store them
├── view_poems.py      # CLI browser for the local database
├── setup.py           # One-shot DB + schema initialisation
├── schema.sql         # PostgreSQL DDL (tables, indexes, views, seed data)
├── requirements.txt
└── .env               # Local credentials (never commit)
```

## API Reference

### `DatabaseConnection` (`conn.py`)

| Method | Description |
|---|---|
| `insert_poem(poem)` | Insert a single poem dict |
| `insert_poems_batch(poems)` | Bulk insert; returns `(success, failed)` |
| `get_all_poems()` | All poems ordered by id |
| `get_poem_by_id(id)` | Single poem or `None` |
| `get_poems_by_author(author)` | Case-insensitive author search |
| `search_poems(term)` | Trigram fuzzy search across title + author |
| `delete_poem(id)` | Delete by id |
| `get_statistics()` | Aggregate counts and top author |

### `PoetryDBClient` (`poetry_client.py`)

| Method | Description |
|---|---|
| `get_random_poems(count=1)` | Fetch random poems |
| `get_authors()` | All author names |
| `get_titles()` | All poem titles |
| `get_poems_by_author(author)` | All poems for one author |


## Sample Output



## Future Improvements Suggestions
Here are the directions you could take this project, grouped by theme:

---

**Data & Storage**
- Add a `poets` table with biographical info (birth year, nationality, era) and link it to poems via a foreign key instead of storing author as a plain string
- Track duplicate detection so re-fetching the same poem from the API doesn't insert it twice
- Add full-text search using PostgreSQL's native `tsvector`/`tsquery` instead of relying solely on trigrams
- Store the raw API JSON response in a separate column for auditing and reprocessing without re-fetching
- Add soft deletes with a `deleted_at` timestamp instead of permanently removing rows

---

**API & Ingestion**
- Schedule `fetch_data.py` to run automatically on a cron job or using APScheduler, building the collection passively over time
- Fetch poems by specific author or title on demand, not just randomly
- Add support for other poetry APIs (e.g. Poetry Foundation, Gutenberg) behind the same `PoetryDBClient` interface
- Implement a sync/diff mechanism that only fetches poems not already in the database
- Rate limiting and retry logic with exponential backoff for flaky network conditions

---

**Analysis & Intelligence**
- Sentiment analysis on poem lines using a library like TextBlob or VADER to tag poems as melancholic, joyful, angry, etc.
- Word frequency and vocabulary richness metrics per author
- Detect rhyme schemes automatically by comparing line endings
- Cluster poems by theme or style using embeddings and k-means
- Identify the most and least complex poems using readability scores

---

**CLI & Interface**
- Interactive TUI (terminal UI) using `textual` or `curses` so you can scroll and select poems without typing commands
- Export a poem to a formatted PDF or plain text file directly from the CLI
- A `random` command that picks and displays a poem of the day from your local collection
- Colour-theme support so users can choose how the output looks

---

**API Layer**
- Wrap the database with a REST API using FastAPI, exposing endpoints like `GET /poems`, `GET /poems/{id}`, `POST /poems`, `DELETE /poems/{id}`
- Add pagination, filtering, and sorting query parameters to list endpoints
- Authentication with API keys so only authorised clients can write data
- A `/stats` endpoint returning live database statistics as JSON

---

**Web Frontend**
- A simple read-only web UI to browse and search the collection in a browser
- A "poem of the day" page that picks a random poem on each visit
- Author pages listing all their stored poems with metadata

---

**Testing & Reliability**
- Unit tests for `insert_poem`, `search_poems`, and the API client using `pytest` and mocked HTTP responses
- Integration tests that spin up a temporary PostgreSQL database using `pytest-postgresql` or Docker
- A CI pipeline (GitHub Actions) that runs linting, type checks, and tests on every push
- Property-based testing with `hypothesis` to throw unexpected data shapes at `insert_poem`

---

**DevOps & Deployment**
- Dockerise the project with a `Dockerfile` and a `docker-compose.yml` that also spins up PostgreSQL
- Environment-specific config files for development, staging, and production
- Database migrations managed by Alembic so schema changes are versioned and reversible
- Secrets management via environment injection rather than a plain `.env` file in production
- Centralised structured logging (JSON format) shipped to a log aggregator like Loki or CloudWatch

---

**Observability**
- Metrics tracking how many poems were fetched, inserted, and failed per run, stored and graphed over time
- Alerting when the API returns errors for several consecutive runs
- A health-check command that verifies both the database connection and the API are reachable



## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [PoetryDB](https://poetrydb.org/) for the wonderful API
- [Gregory-Bot](https://github.com/gregory-bot/data-fetch/) for the code walkthrough
- All the poets whose work is accessible through this API

**Made with ❤️ for poetry lovers and data enthusiasts**