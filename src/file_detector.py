"""
file_detector.py
Detects the file type (JSON/Excel) and API type (REST/SOAP) from the input filename.
Convention: filename must contain _REST or _SOAP (case-insensitive).
"""
import os


def detect(file_path: str) -> dict:
    """
    Analyse the input file path and return metadata.

    Returns:
        dict with keys:
            file_type : 'json' | 'excel'
            api_type  : 'REST' | 'SOAP'
            base_name : filename without extension
    Raises:
        ValueError  if _REST / _SOAP is not found in the filename.
        ValueError  if the file extension is not .json / .xlsx / .xls
    """
    basename = os.path.basename(file_path)
    name_upper = basename.upper()

    # ── Detect API type ────────────────────────────────────────────
    if "_REST" in name_upper:
        api_type = "REST"
    elif "_SOAP" in name_upper:
        api_type = "SOAP"
    else:
        raise ValueError(
            f"Cannot determine API type from filename: '{basename}'.\n"
            "Filename must contain '_REST' or '_SOAP' (e.g. TestSuite_REST.json)."
        )

    # ── Detect file type ───────────────────────────────────────────
    ext = os.path.splitext(basename)[1].lower()
    if ext == ".json":
        file_type = "json"
    elif ext in (".xlsx", ".xls"):
        file_type = "excel"
    else:
        raise ValueError(
            f"Unsupported file extension '{ext}' for '{basename}'.\n"
            "Accepted formats: .json, .xlsx, .xls"
        )

    return {
        "file_type": file_type,
        "api_type": api_type,
        "base_name": os.path.splitext(basename)[0],
    }
