import re
import logging

logger = logging.getLogger(__name__)

class PromptSanitizer:
    """
    Sanitizes user inputs to prevent Prompt Injection and formats them securely for LLMs.
    """
    
    @staticmethod
    def sanitize(input_string: str) -> str:
        """
        Escapes XML/HTML tags in the input to prevent malicious actors from breaking out
        of the designated prompt structure or injecting system instructions.
        """
        if not isinstance(input_string, str):
            return str(input_string) if input_string is not None else ""
            
        # Basic escaping for XML delimiters
        sanitized = input_string.replace("<", "&#60;").replace(">", "&#62;")
        return sanitized

    @staticmethod
    def wrap_in_xml(input_string: str, tag: str) -> str:
        """
        Sanitizes the input and wraps it in an XML tag for safer LLM context passing.
        """
        if not input_string:
            return ""
        sanitized = PromptSanitizer.sanitize(input_string)
        return f"<{tag}>\n{sanitized}\n</{tag}>"


class OutputGuardrail:
    """
    Evaluates LLM output against a blocklist to ensure brand safety and prevent hallucinations (e.g., guarantees).
    """
    
    # Default blocklist of phrases that should trigger a failure
    DEFAULT_BLOCKLIST = [
        r"\b100%\b",
        r"\bguarantee\b",
        r"\bguaranteed\b",
        # Adding a basic email regex to prevent the LLM from hallucinating fake contact emails
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b" 
    ]

    @classmethod
    def evaluate(cls, text: str, blocklist: list[str] | None = None) -> tuple[bool, str]:
        """
        Checks the generated text against blocklist patterns.
        Returns (is_safe: bool, reason: str)
        """
        if not text:
            return True, "Empty text"

        patterns = blocklist if blocklist is not None else cls.DEFAULT_BLOCKLIST

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"OutputGuardrail triggered by pattern: {pattern}")
                return False, f"Output contains restricted pattern: {pattern}"

        return True, "Safe"
