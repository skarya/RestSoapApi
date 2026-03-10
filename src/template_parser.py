"""
template_parser.py
Resolves {{VARIABLE_NAME}} placeholders in any string using environment variables.

Variables are loaded from .env via python-dotenv at module import time.
Unknown variables are replaced with an empty string and a warning is printed.
"""
import os
import re
from dotenv import load_dotenv


# Load .env once when this module is first imported
_env_loaded = False


def _ensure_env_loaded():
    global _env_loaded
    if not _env_loaded:
        import sys
        # 1. Try external .env next to EXE or in project root
        if hasattr(sys, "_MEIPASS"):
            env_path = os.path.join(os.path.dirname(sys.executable), ".env")
        else:
            env_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
            )
            
        # 2. Try bundled .env as fallback if external not found
        if not os.path.isfile(env_path) and hasattr(sys, "_MEIPASS"):
            env_path = os.path.join(sys._MEIPASS, ".env")

        if os.path.isfile(env_path):
            load_dotenv(env_path)
        _env_loaded = True


_PLACEHOLDER_RE = re.compile(r"\{\{([^}]+)\}\}")


def resolve(text: str) -> str:
    """
    Replace all {{VAR}} tokens in *text* with their os.environ values.

    Args:
        text : input string potentially containing {{VAR}} tokens.

    Returns:
        str — text with all resolvable tokens substituted.
    """
    if not text:
        return text

    _ensure_env_loaded()

    def _replacer(match):
        var_name = match.group(1).strip()
        value = os.environ.get(var_name)
        if value is None:
            print(f"  [WARN] Template variable '{{{{{var_name}}}}}' not found in environment. Leaving blank.")
            return ""
        return value

    return _PLACEHOLDER_RE.sub(_replacer, text)
