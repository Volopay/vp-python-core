class BaseAgentException(Exception):
    """Base exception for all agent-related errors."""
    pass

class RetryableAgentException(BaseAgentException):
    """Exception raised when an agent encounters a transient error and should retry."""
    pass

class FatalAgentException(BaseAgentException):
    """Exception raised when an agent encounters a non-recoverable error (e.g., safety violation)."""
    pass

class RequiresHumanReviewException(FatalAgentException):
    """
    Exception raised when an agent exhausts its recursion limit (e.g. failing quality 
    evaluations repeatedly) and requires a human SDR to intervene and manually craft the message.
    """
    def __init__(self, lead_id: str, message: str = "Agent exhausted recursion limit and requires human review."):
        self.lead_id = lead_id
        super().__init__(f"{message} (Lead ID: {lead_id})")
