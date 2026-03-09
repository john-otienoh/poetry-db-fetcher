import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

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

class DatabaseConnection:
    """Handle PostgreSQL database connections"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'poetry_data')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.connection = None
        self.cursor = None
        logger.info(f"Database Connection Initialized for {self.database}")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info(f"Connected to database: {self.database} (autocommit={self.connection.autocommit})")
            return self.connection
        
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
            logger.debug("Cursor closed")

        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute a SQL query
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters
            fetch (bool): Whether to fetch results
            
        Returns:
            list: Query results if fetch=True, else None
        """
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            
            if fetch:
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return None
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            if self.connection and not self.connection.autocommit:
                self.connection.rollback()
            raise

    def insert_poem(self, poem):
        """
        Insert a poem into the database.

        Args:
            poem: Can be a dict, list of dicts, or SimpleNamespace object
        """
        query = """
        INSERT INTO poems (
            title, author, lines, linecount
        ) VALUES (
            %s, %s, %s, %s
        )
        """

        if isinstance(poem, list):
            if len(poem_data) == 0:
                logger.warning("No poem data to insert")
                return False
            poem_data = poem[0]
        elif isinstance(poem, dict):
            poem_data = poem
        else:
            logger.error(f"Expected dict or list, got {type(poem)}")
            return False

        # Extract data safely with .get() for dicts
        title = poem_data.get('title', 'Unknown Title')
        author = poem_data.get('author', 'Unknown Author')

        # Handle lines - ensure it's a list
        lines = poem_data.get('lines', [])
        if lines is None:
            lines = []
        elif isinstance(lines, str):
            lines = [lines]
        lines = list(lines) if lines else []

        # Handle linecount
        linecount = poem_data.get('linecount')
        if linecount is None:
            linecount = len(lines)
        else:
            try:
                linecount = int(linecount)
            except (ValueError, TypeError):
                linecount = len(lines)

        params = (title, author, Json(lines), linecount)

        try:
            self.execute_query(query, params, fetch=False)
            self.connection.commit()
            logger.info(f"Inserted poem: '{title}' by {author} having {linecount} lines.")
            return True
        except Exception as e:
            logger.info(f"Failed to insert poem: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        
    def get_all_poems(self):
        """Retrieve all poems from database"""
        query = "SELECT id, title, author, lines, linecount, created_at FROM poems ORDER BY id"
        return self.execute_query(query) or []
    
    def get_poem_by_id(self, poem_id: int) :
        query = """
        SELECT id, title, author, lines, linecount, created_at
        FROM poems
        WHERE id= %s
        """
        results = self.execute_query(query, (poem_id,))
        return results[0] if results else None
    
    def get_poems_by_author(self, author: str):
        query = """
        SELECT id, title, linecount, created_at
        FROM poems
        WHERE author ILIKE %s
        ORDER BY title
        """
        return self.execute_query(query, (f'%{author}%',)) or []

    def delete_poem(self, poem_id: int):
        query = "DELETE FROM poems WHERE id = %s"
        try:
            self.execute_query(query, (poem_id,), fetch=False)
            logger.info(f"Deleted poem with ID: {poem_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete poem {poem_id}: {e}")
            return False
        
    def insert_poems_batch(self, poems_list):
        """Insert multiple poems in a single transaction."""
        successful = 0
        failed = 0
        
        for poem in poems_list:
            if self.insert_poem(poem):
                successful += 1
            else:
                failed += 1
        
        logger.info(f"✓ Batch insert complete: {successful} successful, {failed} failed")
        return successful, failed
    def get_statistics(self):
        """Get database statistics."""
        stats = {}
        
        # Total poems
        result = self.execute_query("SELECT COUNT(*) as count FROM poems")
        stats['total_poems'] = result[0]['count'] if result else 0
        
        # Total authors
        result = self.execute_query("SELECT COUNT(DISTINCT author) as count FROM poems")
        stats['total_authors'] = result[0]['count'] if result else 0
        if result:
            stats['top_author_count'] = result[0]['count']
        
        return stats
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test database connection
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Test query
        stats = db.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        
        poems = db.get_all_poems()
        if poems:
            print(f"\nPoems in database: {len(poems)}")
            for poem in poems:
                print(f"  - {poem['title']} by {poem['author']} ({poem['linecount']} lines)")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close()
