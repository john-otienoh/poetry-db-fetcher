#!/usr/bin/env python3
import requests
import time
import os
from typing import Dict, List, Optional, Union
import logging
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


class PoetryDBClient:
    """Client for interacting with the PoetryDB API."""
    
    BASE_URL = 'https://poetrydb.org/'
    TIMEOUT = 1000000
    
    # Class constants for endpoints
    ENDPOINT_RANDOM = 'random'
    ENDPOINT_TITLES = 'titles'
    ENDPOINT_AUTHOR = 'author'
    
    def __init__(self):
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Union[Dict, List]:
        """
        Make a request to the PoetryDB API.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary or list
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            response_time = int((time.time() - start_time) * 1000)
            logger.info(f"API Request successful: {endpoint} ({response_time}ms)")
            
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out: {endpoint}")
            raise Exception("API request timed out")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {endpoint} - {e}")
            raise Exception(f"API request failed: {e}")
            
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise Exception(f"Invalid JSON response: {e}")
    
    def get_random_poem(self, count: int = 1) -> List[Dict]:
        """
        Fetch random poem(s) from the PoetryDB API.
        
        Args:
            count: Number of random poems to fetch (default: 1)
            
        Returns:
            List of Poem objects
            
        Raises:
            Exception: If the API request fails
        """
        try:
            endpoint = self.ENDPOINT_RANDOM
            if count > 1:
                endpoint = f"{endpoint}/{count}"

            data =  self._make_request(endpoint=endpoint)
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                return []
        except Exception as e:
            logger.error(f"Error fetching random poem: {e}")
            return []
    
    def get_poem_titles(self) -> List[str]:
        """
        Fetch poem titles.
            
        Returns:
            List of Poem titles
        """
        try:
            endpoint = self.ENDPOINT_TITLES
            data = self._make_request(endpoint)
            
            return data
            
        except Exception as e:
            logging.error(f"Error fetching poem titles: {e}")
            return []
    
    def get_poem_authors(self):
        """
        Fetch poets.
        
        Returns:
            List of poets
        """
        try:
            endpoint = self.ENDPOINT_AUTHOR
            data = self._make_request(endpoint)
            return data
            
        except Exception as e:
            print(f"Error fetching poems by author: {e}")
            return []
    
    def close(self):
        """Close the session."""
        self.session.close()
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

def main():
    """Example usage of the PoetryDBClient."""
    client = PoetryDBClient()
    
    try:
        # Get a random poem
        print("Fetching a random poem...\n")
        poems = client.get_random_poem()
        
        if poems:
            print(poems[0])
        else:
            print("Failed to fetch poem.")

        authors = client.get_poem_authors()
        print(f"\nTotal authors in database: {len(authors)}")


        titles = client.get_poem_titles()
        print(f"\nTotal authors in database: {len(titles)}")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()