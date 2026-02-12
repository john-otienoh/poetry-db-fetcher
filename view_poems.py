#!/usr/bin/env python3
from conn import DatabaseConnection

def check_data():
    with DatabaseConnection() as db:
        # Count poems
        result = db.execute_query("SELECT COUNT(*) as count FROM poems")
        count = result[0]['count'] if result else 0
        print(f"📊 Total poems: {count}")
        
        if count > 0:
            # Show all poems
            poems = db.get_all_poems()
            print(f"\n📚 Poems:")
            for poem in poems:
                print(f"  ID: {poem['id']} - {poem['title']} by {poem['author']} ({poem['linecount']} lines)")
        else:
            print("❌ No poems found in database!")

if __name__ == "__main__":
    check_data()