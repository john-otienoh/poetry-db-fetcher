from poetry_client import PoetryDBClient
from conn import DatabaseConnection
# import sys
import traceback

def fetch_random_poems(count: int = 1):
    """
    Fetch random poems from PoetryDB and store in database.
    
    Args:
        count: Number of random poems to fetch (default: 1)
    """
    print(f"\n🔍 Fetching {count} random poem(s)...")
    
    with PoetryDBClient() as poetry_client:
        with DatabaseConnection() as db:
            try:
                # Fetch poem from API
                poems = poetry_client.get_random_poem(count=count)
                
                if not poems:
                    print("✗ No poems received from API")
                    return False
                
                print(f"✓ Received {len(poems)} poem(s) from API")
                
                # Insert into database
                successful, failed = db.insert_poems_batch(poems)
                
                print(f"\n Results:")
                print(f"  ✓ Successfully inserted: {successful}")
                print(f"  ✗ Failed: {failed}")
                db.connection.commit()
                return successful > 0
                
            except Exception as e:
                print(f"\n✗ Error in fetch_poems: {e}")
                if db.connection:
                    db.connection.rollback()
                traceback.print_exc()
                return False

def main():
    fetch_random_poems(count=1)
    print("\n Done!")


if __name__ == "__main__":
    main()