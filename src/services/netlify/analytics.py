import datetime
import logging
import time
from typing import Any
from typing import Dict

import requests

from src.config import NETLIFY_PAT
from src.config import SITE_ID

_logger = logging.getLogger(__name__)

# --- Analytics API Base URL ---
ANALYTICS_API_BASE_URL = "https://analytics.services.netlify.com/v2"


def get_analytics_data(
    start_time: int = 0,
    end_time: int = 0,
    timezone: str = "America/Los_Angeles",
    resolution: str = "day",
) -> Dict[str, Any]:
    if end_time == 0:
        # (e.g., last 7 days)
        end_time = int(time.time() * 1000)  # Current Unix timestamp in milliseconds
    if start_time == 0:
        # Netlify Analytics typically provides up to 30 days of data [6]
        start_time = int(
            (datetime.datetime.now() - datetime.timedelta(days=30)).timestamp() * 1000
        )

    # Headers for authentication.
    headers = {
        "Authorization": f"Bearer {NETLIFY_PAT}",
        "User-Agent": "Python Netlify Analytics Script",  # Good practice to include a User-Agent
    }
    # Query Parameters.
    params = {
        "from": start_time,
        "to": end_time,
        "timezone": timezone,
        "resolution": resolution,
    }

    result = {}
    # All possible metrics that can be fetched from Netlify Analytics API:
    # 'pageviews', 'visitors', 'bandwidth', 'ranking/countries', ranking/not_found
    # 'ranking/pages', 'ranking/sources'.
    # See URL for more details:
    # https://smhk.net/note/2022/05/collecting-netlify-analytics-data-with-python
    for metric in ["pageviews", "visitors", "bandwidth", "ranking/countries"]:
        try:
            pageviews_url = f"{ANALYTICS_API_BASE_URL}/{SITE_ID}/{metric}"
            response = requests.get(pageviews_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            result[metric] = response.json()
            if metric == "pageviews" or metric == "visitors":
                result[metric]["data"] = result[metric]["data"][:-1]
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching {metric}: {e}")

    return result
