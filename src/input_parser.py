"""
input_parser.py
Parses JSON or Excel input files into a normalised list of TestCase dicts.

Expected columns / keys (case-insensitive matching):
  - TestCaseID
  - Description
  - Method
  - Endpoint
  - Headers       (JSON string or blank)
  - Payload       (inline string, or "file:<filename>" reference)
  - SOAPAction    (for SOAP only; blank for REST)
  - ExpectedStatus (optional, e.g. 200)
"""
import json
import os
import re
import pandas as pd


# Canonical column names → possible aliases in the input file
_COLUMN_ALIASES = {
    "testcaseid":      ["testcaseid", "test_case_id", "tcid", "id", "tc id"],
    "description":     ["description", "desc", "name", "testcasename", "test case name", "title"],
    "method":          ["method", "requestmethod", "httpmethod", "http method"],
    "endpoint":        ["endpoint", "url", "uri", "requesturl", "request url"],
    "headers":         ["headers", "header", "requestheaders", "request headers"],
    "payload":         ["payload", "body", "requestbody", "request body", "requestpayload"],
    "soapaction":      ["soapaction", "soap_action", "action", "operation"],
    "expectedstatus":  ["expectedstatus", "expected_status", "expectedstatuscode", "expectedcode"],
}


def _normalise_key(key: str) -> str:
    """Strip spaces, lower-case a key for alias matching."""
    return re.sub(r"\s+", "", str(key)).lower()


def _map_columns(raw_keys: list) -> dict:
    """
    Build a mapping: canonical_name → raw_column_name.
    Only canonical names that exist in the file are included.
    """
    normalised = {_normalise_key(k): k for k in raw_keys}
    mapping = {}
    for canonical, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalised:
                mapping[canonical] = normalised[alias]
                break
    return mapping


def _build_test_case(row: dict, col_map: dict, api_type: str) -> dict:
    """Convert a raw row dict into a normalised TestCase dict."""
    def get(canonical):
        raw_col = col_map.get(canonical)
        if raw_col is None:
            return ""
        val = row.get(raw_col, "")
        # Treat NaN / None as empty string
        if val is None or (isinstance(val, float) and str(val) == "nan"):
            return ""
        return str(val).strip()

    return {
        "testcaseid":     get("testcaseid")     or f"TC_{id(row)}",
        "description":    get("description"),
        "method":         get("method").upper() or ("POST" if api_type == "SOAP" else "GET"),
        "endpoint":       get("endpoint"),
        "headers":        get("headers"),
        "payload":        get("payload"),
        "soapaction":     get("soapaction"),
        "expectedstatus": get("expectedstatus"),
        "api_type":       api_type,
    }


def parse_file(file_path: str, api_type: str) -> list:
    """
    Parse a JSON or Excel input file and return a list of normalised TestCase dicts.

    Args:
        file_path : absolute path to input file
        api_type  : 'REST' | 'SOAP'  (already detected by file_detector)

    Returns:
        list[dict]  — each dict is a normalised TestCase
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".json":
        return _parse_json(file_path, api_type)
    elif ext in (".xlsx", ".xls"):
        return _parse_excel(file_path, api_type)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _parse_json(file_path: str, api_type: str) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON input file must contain a top-level array of test case objects.")

    if not data:
        return []

    col_map = _map_columns(list(data[0].keys()))
    return [_build_test_case(row, col_map, api_type) for row in data]


def _parse_excel(file_path: str, api_type: str) -> list:
    df = pd.read_excel(file_path, sheet_name=0, dtype=str)
    df = df.where(pd.notnull(df), "")   # replace NaN → ""
    col_map = _map_columns(list(df.columns))
    return [_build_test_case(row, col_map, api_type) for row in df.to_dict(orient="records")]
