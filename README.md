# Poetry Database Fetcher

[![wakatime](https://wakatime.com/badge/user/6d7c48ee-9185-4251-a234-e029aa6b148d/project/4b1f021e-32ba-49c5-937b-91dea0ddfcb6.svg)](https://wakatime.com/badge/user/6d7c48ee-9185-4251-a234-e029aa6b148d/project/4b1f021e-32ba-49c5-937b-91dea0ddfcb6)

[![wakatime](https://wakatime.com/badge/github/john-otienoh/poetry-db-fetcher.svg)](https://wakatime.com/badge/github/john-otienoh/poetry-db-fetcher)

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

```
poetry-db-fetcher/
│
├── .env                    # Environment variables
├── .gitignore             # Git ignore file
├── requirements.txt       # Python dependencies
├── schema.sql            # PostgreSQL schema
│
├── conn.py               # Database connection handler
├── poetry_client.py      # PoetryDB API client
├── fetch_data.py         # Main data fetching script
├── view_poems.py         # Poem viewer utility
└── setup.py             # Database setup script
```

### Module Descriptions

| File | Description |
|------|-------------|
| `conn.py` | PostgreSQL connection manager with context support |
| `poetry_client.py` | PoetryDB API wrapper with error handling |
| `fetch_data.py` | Main script to fetch and store poems |
| `view_poems.py` | CLI tool to view and search poems |
| `setup_database.py` | One-click database setup |

## API Reference

### PoetryDBClient

| Method | Description | Returns |
|--------|-------------|---------|
| `get_random_poem(count=1)` | Fetch random poem(s) | `List[Dict]` |
| `get_poems_by_author(author)` | Fetch poems by author | `List[Dict]` |
| `get_poem_by_title(title)` | Fetch poem by title | `List[Dict]` |
| `get_all_titles()` | Get all poem titles | `List[str]` |
| `get_all_authors()` | Get all authors | `List[str]` |

### DatabaseConnection

| Method | Description | Returns |
|--------|-------------|---------|
| `insert_poem(poem_data)` | Insert single poem | `bool` |
| `insert_poems_batch(poems)` | Insert multiple poems | `(success, failed)` |
| `get_all_poems()` | Get all poems | `List[Dict]` |
| `get_poem_by_id(id)` | Get poem by ID | `Dict` |
| `search_poems(term)` | Search by title/author | `List[Dict]` |
| `get_poems_by_author(author)` | Get poems by author | `List[Dict]` |
| `delete_poem(id)` | Delete poem | `bool` |

## Troubleshooting

### "No poems found in database" after insertion

**Fix:** Enable autocommit in `conn.py`:

```python
def connect(self):
    self.connection = psycopg2.connect(...)
    self.connection.autocommit = True  # Add this line!
```

### "Relation 'poems' does not exist"

**Fix:** Run the database setup:
```bash
python setup_database.py
```

### Connection refused

**Check:**
1. Is PostgreSQL running? `sudo systemctl status postgresql`
2. Are credentials correct in `.env`?
3. Can you connect manually? `psql -U postgres -d poetry_data`

### API rate limiting

PoetryDB is free but has rate limits. Add delays between requests:
```python
import time
time.sleep(1)  # 1 second delay
```

## Running Tests

```bash
# Test database connection
python conn.py

# Test API connection
python poetry_client.py

# Test setup
python setup.py
```

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

## Sample Output

```
============================================================
POETRY DATABASE FETCHER
============================================================

Database Statistics:
  Total poems: 0

Fetching 1 random poem(s)...
✓ API Request successful: random (234ms)
✓ Received 1 poem(s) from API

  First poem received:
  Title: "Hope" is the thing with feathers
  Author: Emily Dickinson
  Linecount: 12
  Lines: 12

✓ Inserted poem: '"Hope" is the thing with feathers' by Emily Dickinson (12 lines)
✓ Batch insert complete: 1 successful, 0 failed

Total poems in database after insert: 1

Done!
```

---

**Made with ❤️ for poetry lovers and data enthusiasts**