"""
payload_loader.py
Resolves payload references to their actual string content.

Supports two formats:
  1. Inline  — any string that does NOT start with "file:"
               → returned as-is
  2. File    — "file:<filename>"  (e.g. "file:create_post.json")
               → reads from data/payloads/<filename>
"""
import os


def _payloads_dir() -> str:
    """
    Locate the data/payloads directory.
    Priority:
      1. External directory next to the EXE/script (for easy user editing)
      2. Bundled directory in _MEIPASS (fallback)
    """
    import sys
    # Base directory for external files
    if hasattr(sys, "_MEIPASS"):
        exe_dir = os.path.dirname(sys.executable)
        bundle_dir = sys._MEIPASS
    else:
        # Dev mode: root of project
        exe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bundle_dir = None

    external_path = os.path.join(exe_dir, "data", "payloads")
    
    # If the folder exists on disk (external), use it!
    if os.path.isdir(external_path):
        return external_path
    
    # Fallback to internal bundle if available
    if bundle_dir:
        return os.path.join(bundle_dir, "data", "payloads")

    return external_path


def load_payload(ref: str) -> str:
    """
    Resolve a payload reference string.

    Args:
        ref : raw payload string from input file.
              Use "file:<filename>" to reference an external payload file.

    Returns:
        str — the final payload content ready to send in the request.
    """
    if not ref:
        return ""

    ref = ref.strip()

    if ref.lower().startswith("file:"):
        filename = ref[5:].strip()  # everything after "file:"
        payloads_dir = _payloads_dir()
        full_path = os.path.join(payloads_dir, filename)

        if not os.path.isfile(full_path):
            raise FileNotFoundError(
                f"Payload file not found: '{full_path}'\n"
                f"Make sure '{filename}' exists in the data/payloads/ folder."
            )

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Inline payload — return as-is
    return ref
