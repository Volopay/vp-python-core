import json
import re
from datetime import datetime
from typing import Any, cast

from vp_core.logging.logger import setup_logger

logger = setup_logger()


def _deep_parse_json(obj: Any) -> Any:
    """
    Recursively traverses a data structure and parses any string that is a valid
    JSON object or array.
    """
    if isinstance(obj, dict):
        return {
            str(k): _deep_parse_json(v) for k, v in cast(dict[Any, Any], obj).items()
        }
    if isinstance(obj, list):
        return [_deep_parse_json(elem) for elem in cast(list[Any], obj)]
    if isinstance(obj, str):
        try:
            # Attempt to parse the string as JSON
            parsed_obj = json.loads(obj)
            # If successful, recurse into the parsed object
            return _deep_parse_json(parsed_obj)
        except (json.JSONDecodeError, TypeError):
            # If it's not a valid JSON string, return it as is
            return obj
    return obj


def parse_llm_output(output: str | None) -> dict[Any, Any] | list[Any]:
    """
    Extract and deeply parse a JSON object or array from LLM output.
    Supports:
    1. JSON inside ```json ... ``` blocks
    2. Inline JSON (top-level {...} or [...])
    3. Escaped JSON strings (e.g., '\\n{\\n  ... }\\n')
    4. Nested JSON strings within the main JSON object.
    """
    if output is None:
        return {}
    try:
        # 1. Try to extract from ```json ... ``` blocks
        match = re.search(r"```json\s*(.*?)\s*```", output, re.DOTALL)
        if not match:
            # 2. Fallback: any top-level {...} or [...] block
            match = re.search(r"(\{.*?\}|\[.*?\])", output, re.DOTALL)

        json_str = ""
        if match:
            json_str = match.group(1).strip()
        else:
            # 3. Final fallback: maybe the whole string *is* the JSON
            json_str = output.strip()

        try:
            parsed_json = json.loads(json_str)
        except json.JSONDecodeError:
            # Try decoding escape characters and re-parse
            decoded = json_str.encode().decode("unicode_escape").strip()
            parsed_json = json.loads(decoded)

        # Deep parse the resulting object
        result = _deep_parse_json(parsed_json)
        if isinstance(result, dict | list):
            return result
        return {}

    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM output: {e}")
        logger.error("Raw output was:\n%s", output)
        return {}


def fetch_urls(output: str) -> list[str]:
    return re.findall(r"https?://[^\s,']+", output)


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime objects.
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
