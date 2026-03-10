"""
executor.py
Orchestrates test case execution in either serial or parallel mode.

Serial   : Runs each test case one at a time using synchronous clients.
Parallel : Fires all test cases concurrently using asyncio + aiohttp.

Each result dict is augmented with:
  - testcaseid      (echoed from input)
  - api_type        (REST | SOAP)
  - pass_fail       PASS / FAIL / ERROR
"""
import asyncio
import aiohttp

from src.rest_client import send_rest, send_rest_async
from src.soap_client import send_soap, send_soap_async
from src.payload_loader import load_payload
from src.template_parser import resolve


def _prepare(tc: dict) -> dict:
    """
    Resolve template variables and load external payloads for a test case.
    Returns a prepared copy of the test case.
    """
    prepared = dict(tc)
    # Resolve endpoint and headers for {{VAR}} tokens
    prepared["endpoint"] = resolve(tc.get("endpoint", ""))
    prepared["headers"]  = resolve(tc.get("headers", ""))

    # Load and resolve payload
    raw_payload = tc.get("payload", "")
    try:
        loaded_payload = load_payload(raw_payload)
    except FileNotFoundError as e:
        print(f"  [WARN] {e}")
        loaded_payload = ""
    prepared["payload"] = resolve(loaded_payload)

    return prepared


def _evaluate(tc: dict, result: dict) -> dict:
    """Compute PASS / FAIL / ERROR and merge back into the result dict."""
    error     = result.get("error", "")
    status_code = result.get("status_code", 0)
    expected  = tc.get("expectedstatus", "")

    if error:
        pass_fail = "ERROR"
    elif expected:
        try:
            pass_fail = "PASS" if status_code == int(expected) else "FAIL"
        except ValueError:
            pass_fail = "PASS" if str(status_code).startswith("2") else "FAIL"
    else:
        # No expected status — treat any 2xx as PASS
        pass_fail = "PASS" if 200 <= status_code < 300 else "FAIL"

    result["testcaseid"]  = tc.get("testcaseid", "")
    result["description"] = tc.get("description", "")
    result["api_type"]    = tc.get("api_type", "")
    result["method"]      = tc.get("method", "")
    result["endpoint"]    = tc.get("endpoint", "")
    result["payload_sent"] = tc.get("payload", "")
    result["pass_fail"]   = pass_fail
    return result


# ── Serial execution ──────────────────────────────────────────────────────────

def _run_serial(test_cases: list) -> list:
    results = []
    total = len(test_cases)
    for idx, tc in enumerate(test_cases, start=1):
        print(f"  [{idx}/{total}] Running {tc['api_type']} › {tc['testcaseid']} [{tc['method']}] ...", end=" ", flush=True)
        prepared = _prepare(tc)
        if tc["api_type"] == "REST":
            result = send_rest(prepared)
        else:
            result = send_soap(prepared)
        final = _evaluate(prepared, result)
        status_label = f"\033[92mPASS\033[0m" if final["pass_fail"] == "PASS" else f"\033[91m{final['pass_fail']}\033[0m"
        print(f"{status_label}  ({result['response_time_ms']} ms)")
        results.append(final)
    return results


# ── Parallel execution ────────────────────────────────────────────────────────

async def _run_parallel_async(test_cases: list) -> list:
    prepared_cases = [_prepare(tc) for tc in test_cases]

    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:

        async def _execute_one(prepared, idx, total):
            tc_id  = prepared.get("testcaseid", f"TC_{idx}")
            method = prepared.get("method", "")
            api    = prepared.get("api_type", "REST")
            print(f"  [{idx}/{total}] ⚡ Parallel {api} › {tc_id} [{method}] ...", flush=True)

            if api == "REST":
                result = await send_rest_async(session, prepared)
            else:
                result = await send_soap_async(session, prepared)

            return _evaluate(prepared, result)

        total = len(prepared_cases)
        tasks = [
            _execute_one(tc, idx, total)
            for idx, tc in enumerate(prepared_cases, start=1)
        ]
        return await asyncio.gather(*tasks)


def _run_parallel(test_cases: list) -> list:
    return asyncio.run(_run_parallel_async(test_cases))


# ── Public entry point ────────────────────────────────────────────────────────

def run(test_cases: list, parallel: bool = False) -> list:
    """
    Execute all test cases and return enriched result dicts.

    Args:
        test_cases : list of normalised TestCase dicts
        parallel   : if True, execute concurrently via asyncio

    Returns:
        list[dict] — one result dict per test case
    """
    if not test_cases:
        print("  [WARN] No test cases to execute.")
        return []

    mode = "PARALLEL ⚡" if parallel else "SERIAL 🔁"
    print(f"\n  Execution mode : {mode}")
    print(f"  Test cases     : {len(test_cases)}\n")

    if parallel:
        return _run_parallel(test_cases)
    else:
        return _run_serial(test_cases)
