from typing import Any, Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor

from config import DBConfig, get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages a single PostgreSQL connection with convenience query methods."""

    def __init__(self, config: Optional[DBConfig] = None) -> None:
        self._cfg = config or DBConfig()
        self._conn: Optional[psycopg2.extensions.connection] = None
        self._cursor: Optional[psycopg2.extensions.cursor] = None

    def connect(self) -> None:
        """Open the database connection."""
        self._conn = psycopg2.connect(**self._cfg.as_dict())
        self._conn.autocommit = True
        self._cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        logger.info("Connected to database '%s'", self._cfg.name)

    def close(self) -> None:
        """Close cursor and connection gracefully."""
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            logger.info("Database connection closed")

    def __enter__(self) -> "DatabaseConnection":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


    def _execute(self, query: str, params: tuple = (), *, fetch: bool = True) -> list[dict]:
        """
        Execute *query* and return rows when fetch=True, else an empty list.
        Raises any psycopg2 exception to the caller.
        """
        if not self._conn:
            self.connect()
        self._cursor.execute(query, params)
        return list(self._cursor.fetchall()) if fetch else []


    def insert_poem(self, poem: dict) -> bool:
        """
        Insert a single poem dict.  Returns True on success.
        Accepts raw API response dicts (title, author, lines, linecount).
        """
        if not isinstance(poem, dict):
            logger.error("insert_poem expects a dict, got %s", type(poem))
            return False

        title = poem.get("title") or "Unknown Title"
        author = poem.get("author") or "Unknown Author"
        lines = poem.get("lines") or []
        if isinstance(lines, str):
            lines = [lines]
        lines = list(lines)

        raw_lc = poem.get("linecount")
        try:
            linecount = int(raw_lc) if raw_lc is not None else len(lines)
        except (ValueError, TypeError):
            linecount = len(lines)

        query = """
            INSERT INTO poems (title, author, lines, linecount)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self._execute(query, (title, author, Json(lines), linecount), fetch=False)
            logger.info("Inserted '%s' by %s (%d lines)", title, author, linecount)
            return True
        except Exception as exc:
            logger.error("Failed to insert poem '%s': %s", title, exc)
            return False

    def insert_poems_batch(self, poems: list[dict]) -> tuple[int, int]:
        """Insert a list of poem dicts. Returns (success_count, failure_count)."""
        success = sum(1 for p in poems if self.insert_poem(p))
        failed = len(poems) - success
        logger.info("Batch insert complete: %d succeeded, %d failed", success, failed)
        return success, failed

    def get_all_poems(self) -> list[dict]:
        """Return all poems ordered by id."""
        return self._execute(
            "SELECT id, title, author, lines, linecount, created_at FROM poems ORDER BY id"
        )

    def get_poem_by_id(self, poem_id: int) -> Optional[dict]:
        """Return a single poem by primary key, or None."""
        rows = self._execute(
            "SELECT id, title, author, lines, linecount, created_at FROM poems WHERE id = %s",
            (poem_id,),
        )
        return rows[0] if rows else None

    def get_poems_by_author(self, author: str) -> list[dict]:
        """Case-insensitive author search using ILIKE."""
        return self._execute(
            "SELECT id, title, author, linecount, created_at FROM poems WHERE author ILIKE %s ORDER BY title",
            (f"%{author}%",),
        )

    def search_poems(self, term: str) -> list[dict]:
        """
        Full-text search across title and author using pg_trgm similarity.
        Falls back to ILIKE if trigram extension is unavailable.
        """
        query = """
            SELECT id, title, author, linecount,
                   similarity(title, %s)  AS title_sim,
                   similarity(author, %s) AS author_sim
            FROM poems
            WHERE title  % %s
               OR author % %s
            ORDER BY GREATEST(similarity(title, %s), similarity(author, %s)) DESC
        """
        try:
            return self._execute(query, (term, term, term, term, term, term))
        except Exception:
            logger.warning("pg_trgm unavailable, falling back to ILIKE search")
            return self._execute(
                "SELECT id, title, author, linecount FROM poems "
                "WHERE title ILIKE %s OR author ILIKE %s ORDER BY title",
                (f"%{term}%", f"%{term}%"),
            )

    def delete_poem(self, poem_id: int) -> bool:
        """Delete a poem by id. Returns True on success."""
        try:
            self._execute("DELETE FROM poems WHERE id = %s", (poem_id,), fetch=False)
            logger.info("Deleted poem id=%d", poem_id)
            return True
        except Exception as exc:
            logger.error("Failed to delete poem id=%d: %s", poem_id, exc)
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Return a dict of aggregate stats about the poems table."""
        rows = self._execute("""
            SELECT
                COUNT(*)                          AS total_poems,
                COUNT(DISTINCT author)            AS total_authors,
                COALESCE(AVG(linecount), 0)::int  AS avg_lines,
                COALESCE(SUM(linecount), 0)       AS total_lines
            FROM poems
        """)
        stats: dict[str, Any] = dict(rows[0]) if rows else {}
        top = self._execute("""
            SELECT author, COUNT(*) AS poem_count
            FROM poems
            GROUP BY author
            ORDER BY poem_count DESC
            LIMIT 1
        """)
        if top:
            stats["top_author"] = top[0]["author"]
            stats["top_author_count"] = top[0]["poem_count"]

        return stats