import sys

from config import get_logger
from conn import DatabaseConnection
from poetry_client import PoetryDBClient

logger = get_logger(__name__)

def fetch_random_poems(count: int = 10):
    """
    Fetch random poems from PoetryDB and store in database.
    
    Args:
        count: Number of random poems to fetch (default: 1)
    """
    logger.info("Fetching %d random poem(s) from PoetryDB…", count)

    with PoetryDBClient() as client:
        poems = client.get_random_poem(count=count)

    if not poems:
        logger.warning("API returned no poems.")
        return False

    logger.info("Received %d poem(s) from API", len(poems))

    with DatabaseConnection() as db:
        success, failed = db.insert_poems_batch(poems)
        stats = db.get_statistics()

    logger.info("Stored %d poem(s), %d failed.", success, failed)
    logger.info("Database now holds %d poem(s).", stats.get("total_poems", "?"))
    return success > 0

def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    ok = fetch_random_poems(count)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()