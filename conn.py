import psycopg2
from psycopg2.extras import RealDictCursor
import os
from psycopg2.extras import Json
from dotenv import load_dotenv
from types import SimpleNamespace

# Load environment variables
load_dotenv()

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
            print(f"Connected to database: {self.database}")
            return self.connection
        
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
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
            print(f"✗ Query execution failed: {e}")
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
                print("✗ No poem data to insert")
                return False
            poem_data = poem[0]
        elif isinstance(poem, dict):
            # Convert SimpleNamespace to dict
            poem_data = poem
        else:
            print(f"✗ Expected dict or list, got {type(poem)}")
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
            print(f"✓ Inserted poem: '{title}' by {author} having {linecount} lines.")
            return True
        except Exception as e:
            print(f"✗ Failed to insert poem: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        
    def get_all_poems(self):
        """Retrieve all poems from database"""
        query = "SELECT id, title, author, lines, linecount, created_at FROM poems ORDER BY id"
        return self.execute_query(query)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def insert_poems_batch(self, poems_list):
        """Insert multiple poems in a single transaction."""
        successful = 0
        failed = 0
        
        for poem in poems_list:
            if self.insert_poem(poem):
                successful += 1
            else:
                failed += 1
        
        print(f"✓ Batch insert complete: {successful} successful, {failed} failed")
        return successful, failed

if __name__ == "__main__":
    # Test database connection
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Test query
        results = db.execute_query("SELECT COUNT(*) as count FROM poems")
        if results:
            count = results[0]['count']
            print(f"Total poems in database: {count}")
        
        poems = db.get_all_poems()
        if poems:
            print(f"\nPoems in database:")
            for poem in poems:
                print(f"  - {poem['title']} by {poem['author']} ({poem['linecount']} lines)")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close()
