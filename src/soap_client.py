"""
soap_client.py
Executes SOAP API calls by POSTing raw XML envelopes.

No WSDL parsing — user supplies the full SOAP envelope in the payload field.
Supports both synchronous (serial) and asynchronous (parallel) execution.

Each call returns a result dict:
  status_code     : int
  response_body   : str  (raw XML response)
  response_time_ms: float
  error           : str
"""
import time
import requests
import aiohttp
import asyncio

TIMEOUT_SECONDS = 30


def _build_soap_headers(raw_headers: str, soap_action: str) -> dict:
    """Build headers for SOAP request, merging user headers with required SOAP headers."""
    import json
    base = {
        "Content-Type": "text/xml; charset=utf-8",
    }
    if soap_action:
        base["SOAPAction"] = f'"{soap_action}"'

    if raw_headers:
        try:
            user_headers = json.loads(raw_headers)
            base.update(user_headers)
        except (json.JSONDecodeError, TypeError):
            pass

    return base


# ── Synchronous (serial) ──────────────────────────────────────────────────────

def send_soap(tc: dict) -> dict:
    """
    Execute a single SOAP request synchronously.

    Args:
        tc : normalised TestCase dict

    Returns:
        result dict
    """
    endpoint    = tc.get("endpoint", "")
    payload     = tc.get("payload", "")
    soap_action = tc.get("soapaction", "")
    headers     = _build_soap_headers(tc.get("headers", ""), soap_action)

    if not payload:
        return _error_result("SOAP payload is empty. Provide a complete XML envelope.", 0)

    start = time.monotonic()
    try:
        resp = requests.post(
            endpoint,
            data=payload.encode("utf-8"),
            headers=headers,
            timeout=TIMEOUT_SECONDS,
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

async def send_soap_async(session: aiohttp.ClientSession, tc: dict) -> dict:
    """
    Execute a single SOAP request asynchronously.

    Args:
        session : shared aiohttp.ClientSession
        tc      : normalised TestCase dict

    Returns:
        result dict
    """
    endpoint    = tc.get("endpoint", "")
    payload     = tc.get("payload", "")
    soap_action = tc.get("soapaction", "")
    headers     = _build_soap_headers(tc.get("headers", ""), soap_action)

    if not payload:
        return _error_result("SOAP payload is empty. Provide a complete XML envelope.", 0)

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    start = time.monotonic()
    try:
        async with session.post(
            endpoint,
            data=payload.encode("utf-8"),
            headers=headers,
            timeout=timeout,
        ) as resp:
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
