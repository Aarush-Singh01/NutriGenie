"""
IBM Granite API client for NutriGenie.

Calls POST /ml/v1/text/generation on IBM watsonx.ai using IAM token exchange.
Falls back to a clearly-labelled stub response when credentials are absent (dev mode).
"""

import logging
import time
from typing import Optional

import requests

from config import settings

logger = logging.getLogger(__name__)

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
GENERATION_PATH = "/ml/v1/text/generation"
API_VERSION = "2023-05-29"
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 2

_iam_token_cache: dict = {"token": None, "expires_at": 0}


def _get_iam_token() -> Optional[str]:
    """Exchange IBM Cloud API key for an IAM bearer token (cached for ~50 min)."""
    if not settings.watsonx_api_key:
        return None

    now = time.time()
    if _iam_token_cache["token"] and _iam_token_cache["expires_at"] > now + 60:
        return _iam_token_cache["token"]

    try:
        resp = requests.post(
            IAM_TOKEN_URL,
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": settings.watsonx_api_key,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        token = data["access_token"]
        expires_in = int(data.get("expires_in", 3600))
        _iam_token_cache["token"] = token
        _iam_token_cache["expires_at"] = now + expires_in
        return token
    except Exception as exc:
        logger.error("IAM token exchange failed: %s", exc)
        return None


def generate(prompt: str, max_new_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Call IBM Granite via watsonx.ai REST API and return the generated text.

    If credentials are absent or the API is unreachable, returns a fallback
    response clearly labelled as '[FALLBACK — No IBM credentials configured]'.
    """
    token = _get_iam_token()
    if not token or not settings.watsonx_project_id:
        return _fallback_response(prompt)

    #url = settings.watsonx_url.rstrip("/") + GENERATION_PATH
    url = settings.watsonx_url.rstrip("/") + GENERATION_PATH + "?version=" + API_VERSION
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model_id": settings.watsonx_model_id,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy" if temperature == 0 else "sample",
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "repetition_penalty": 1.1,
        },
        "project_id": settings.watsonx_project_id,
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if results:
                return results[0].get("generated_text", "").strip()
            return ""
        except requests.exceptions.Timeout:
            last_error = "Granite API timeout"
            logger.warning("Granite API attempt %d/%d timed out.", attempt, MAX_RETRIES)
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            last_error = f"Granite API HTTP {status}"
            logger.error("Granite API HTTP error: %s", exc)
            if status in (401, 403):
                break  # No point retrying auth errors
        except Exception as exc:
            last_error = str(exc)
            logger.error("Granite API error (attempt %d): %s", attempt, exc)

        if attempt < MAX_RETRIES:
            time.sleep(2)

    logger.warning("All Granite API attempts failed. Using fallback. Last error: %s", last_error)
    return _fallback_response(prompt, error=last_error)


def _fallback_response(prompt: str, error: Optional[str] = None) -> str:
    """
    Return a structured fallback when Granite is unavailable.
    This is clearly labelled so users know they are seeing cached/general data.
    """
    notice = error if error else "IBM watsonx credentials not configured"
    return (
        f"[FALLBACK — AI service unavailable: {notice}]\n\n"
        "I can provide general nutrition information based on my knowledge base, "
        "but personalized AI-generated advice is temporarily unavailable.\n\n"
        "Please ensure your IBM watsonx credentials are correctly configured in .env, "
        "or try again later."
    )
