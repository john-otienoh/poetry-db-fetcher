#!/usr/bin/env python3
import requests
from config import APIConfig, get_logger

logger = get_logger(__name__)


class PoetryDBClient:
    """Client for interacting with the PoetryDB API."""

    def __init__(self, config: APIConfig | None = None):
        self._cfg = config or APIConfig()
        self._session = requests.Session()
    
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self._session.close()

    def _get(self, path: str):
        """
        GET {base_url}/{path} and return the parsed JSON.
        Raises RuntimeError on any network or HTTP failure.
        """
        url = f"{self._cfg.base_url}{path}"
        try:
            response = self._session.get(url, timeout=self._cfg.timeout)
            response.raise_for_status()
            logger.debug("GET %s -> %d", url, response.status_code)
            return response.json()
        except requests.Timeout:
            raise RuntimeError(f"Request timed out: {url}")
        except requests.RequestException as exc:
            raise RuntimeError(f"Request failed: {url} — {exc}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Invalid JSON from {url}: {exc}") from exc
    
    def get_random_poem(self, count: int = 1):
        """
        Fetch random poem(s) from the PoetryDB API.
        
        Args:
            count: Number of random poems to fetch (default: 1)
            
        Returns:
            List of Poem objects
            
        Raises:
            Exception: If the API request fails
        """
        path = "random" if count == 1 else f"random/{count}"
        try:
            data = self._get(path)
            if isinstance(data, dict):
                return [data]
            if isinstance(data, list):
                return data
            logger.warning("Unexpected response type from API: %s", type(data))
            return []
        except RuntimeError as exc:
            logger.error("get_random_poems failed: %s", exc)
            return []
    
    def get_poem_titles(self):
        """
        Fetch poem titles.
            
        Returns:
            List of Poem titles
        """
        try:
            data = self._get("title")
            return data.get("titles", []) if isinstance(data, dict) else []
        except RuntimeError as exc:
            logger.error("get_titles failed: %s", exc)
            return []

    
    def get_poem_authors(self):
        """
        Fetch poets.
        Returns:
            List of poets
        """
        try:
            data = self._get("author")
            return data.get("authors", []) if isinstance(data, dict) else []
        except RuntimeError as exc:
            logger.error("get_authors failed: %s", exc)
            return []
    