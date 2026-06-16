"""
Reusable API Client with retry logic, timeout handling, and error management.
"""

import time
import logging
import requests
from typing import Optional, Dict, Any, Callable
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Custom exception for API client errors."""
    pass


class RateLimitError(APIClientError):
    """Raised when rate limit is hit."""
    pass


class APIClient:
    """
    HTTP client for external API integration.
    
    Features:
        - Automatic retries with exponential backoff
        - Timeout handling
        - Response validation
        - Error logging
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoMarketTracker/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Internal method to make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            retry_count: Current retry attempt number
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            APIClientError: On unrecoverable errors
            RateLimitError: On 429 status code
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {params}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                logger.warning(f"Rate limit hit. Retry after {retry_after}s")
                if retry_count < self.max_retries:
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, params, retry_count + 1)
                raise RateLimitError(f"Rate limit exceeded after {self.max_retries} retries")
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
                raise APIClientError(f"Failed to parse JSON response: {e}")
                
        except Timeout as e:
            logger.error(f"Request timeout for {url}: {e}")
            if retry_count < self.max_retries:
                wait_time = self.backoff_factor * (2 ** retry_count)
                logger.info(f"Retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self._make_request(method, endpoint, params, retry_count + 1)
            raise APIClientError(f"Request timeout after {self.max_retries} retries: {e}")
            
        except ConnectionError as e:
            logger.error(f"Connection error for {url}: {e}")
            if retry_count < self.max_retries:
                wait_time = self.backoff_factor * (2 ** retry_count)
                time.sleep(wait_time)
                return self._make_request(method, endpoint, params, retry_count + 1)
            raise APIClientError(f"Connection failed after {self.max_retries} retries: {e}")
            
        except RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise APIClientError(f"API request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        return self._make_request("GET", endpoint, params)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()