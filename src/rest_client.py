"""
rest_client.py
Executes REST API calls in both synchronous (serial) and asynchronous (parallel) modes.

Sync  : uses 'requests'  — simple, blocking
Async : uses 'aiohttp'   — non-blocking, for parallel execution

Each call returns a result dict:
  status_code     : int  HTTP status code (0 on connection error)
  response_body   : str  response text
  response_time_ms: float  round-trip time in milliseconds
  error           : str  error message if exception occurred, else ""
"""
import json
import time
import requests
import aiohttp
import asyncio


TIMEOUT_SECONDS = 30


def _build_headers(raw_headers: str) -> dict:
    """Parse JSON headers string into dict. Returns empty dict on failure."""
    if not raw_headers:
        return {}
    try:
        return json.loads(raw_headers)
    except (json.JSONDecodeError, TypeError):
        print(f"  [WARN] Could not parse headers as JSON: {raw_headers!r}")
        return {}


def _build_body(method: str, payload: str) -> dict:
    """
    Return kwargs for requests/aiohttp body argument.
    Auto-detects JSON vs XML/plain-text payload.
    """
    if not payload or method.upper() in ("GET", "DELETE"):
        return {}
    try:
        parsed = json.loads(payload)
        return {"json": parsed}
    except (json.JSONDecodeError, TypeError):
        return {"data": payload}


# ── Synchronous (serial) ──────────────────────────────────────────────────────

def send_rest(tc: dict) -> dict:
    """
    Execute a single REST request synchronously.

    Args:
        tc : normalised TestCase dict from input_parser

    Returns:
        result dict
    """
    method   = tc.get("method", "GET").upper()
    endpoint = tc.get("endpoint", "")
    headers  = _build_headers(tc.get("headers", ""))
    payload  = tc.get("payload", "")
    body_kwargs = _build_body(method, payload)

    start = time.monotonic()
    try:
        resp = requests.request(
            method,
            endpoint,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            **body_kwargs,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "status_code":      resp.status_code,
            "response_body":    resp.text,
            "response_time_ms": round(elapsed_ms, 2),
            "error":            "",
        }
    except requests.exceptions.Timeout:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Request timed out after {TIMEOUT_SECONDS}s", elapsed_ms)
    except requests.exceptions.ConnectionError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Connection error: {e}", elapsed_ms)
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Unexpected error: {e}", elapsed_ms)


# ── Asynchronous (parallel) ───────────────────────────────────────────────────

async def send_rest_async(session: aiohttp.ClientSession, tc: dict) -> dict:
    """
    Execute a single REST request asynchronously via aiohttp.

    Args:
        session  : shared aiohttp.ClientSession
        tc       : normalised TestCase dict

    Returns:
        result dict
    """
    method   = tc.get("method", "GET").upper()
    endpoint = tc.get("endpoint", "")
    headers  = _build_headers(tc.get("headers", ""))
    payload  = tc.get("payload", "")

    # Build request body
    if payload and method not in ("GET", "DELETE"):
        try:
            body = json.loads(payload)
            kwargs = {"json": body}
        except (json.JSONDecodeError, TypeError):
            kwargs = {"data": payload}
    else:
        kwargs = {}

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    start = time.monotonic()
    try:
        async with session.request(method, endpoint, headers=headers, timeout=timeout, **kwargs) as resp:
            body_text = await resp.text()
            elapsed_ms = (time.monotonic() - start) * 1000
            return {
                "status_code":      resp.status,
                "response_body":    body_text,
                "response_time_ms": round(elapsed_ms, 2),
                "error":            "",
            }
    except asyncio.TimeoutError:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Request timed out after {TIMEOUT_SECONDS}s", elapsed_ms)
    except aiohttp.ClientConnectionError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Connection error: {e}", elapsed_ms)
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return _error_result(f"Unexpected error: {e}", elapsed_ms)


def _error_result(message: str, elapsed_ms: float) -> dict:
    return {
        "status_code":      0,
        "response_body":    message,
        "response_time_ms": round(elapsed_ms, 2),
        "error":            message,
    }
