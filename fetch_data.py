from poetry_client import PoetryDBClient
from conn import DatabaseConnection
import logging
import traceback
import os
from datetime import datetime

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, f'poetry_db_{datetime.now().strftime("%Y%m%d")}.log')

# Configure logging to file
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename)
    ]
)

logger = logging.getLogger(__name__)

def fetch_random_poems(count: int = 1):
    """
    Fetch random poems from PoetryDB and store in database.
    
    Args:
        count: Number of random poems to fetch (default: 1)
    """
    print(f"\n Fetching {count} random poem(s)...")
    
    with PoetryDBClient() as poetry_client:
        with DatabaseConnection() as db:
            try:
                # Fetch poem from API
                poems = poetry_client.get_random_poem(count=count)
                
                if not poems:
                    logger.warning("No poems received from API")
                    return False
                
                logger.info(f"Received {len(poems)} poem(s) from API")
                
                # Insert into database
                successful, failed = db.insert_poems_batch(poems)
                
                logger.info(f"\n Results:")
                logger.info(f"Successfully inserted: {successful}")
                logger.info(f"Failed: {failed}")
                stats = db.get_statistics()
                logger.info(f"Total poems in database: {stats['total_poems']}")
                return successful > 0
                
            except Exception as e:
                logger.error(f"\n✗ Error in fetch_poems: {e}")
                if db.connection:
                    db.connection.rollback()
                traceback.print_exc()
                return False

def main():
    fetch_random_poems(count=10)
    print("\n Done!")


if __name__ == "__main__":
    main()