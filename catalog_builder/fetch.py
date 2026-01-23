import requests
from .config import USER_AGENT, REQUEST_TIMEOUT


def fetch_page(url: str) -> str:
    """
    Fetch a web page and return its HTML content.

    Args:
        url (str): Full URL to fetch

    Returns:
        str: HTML content of the page

    Raises:
        HTTPError: If the request fails
    """
    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text
