"""Custom exceptions for the application"""


class EmailAutomatorException(Exception):
    """Base exception for email automator"""

    pass


class EmailProviderError(EmailAutomatorException):
    """Email provider related errors"""

    pass


class RateLimitExceeded(EmailAutomatorException):
    """Rate limit exceeded"""

    pass


class InvalidEmailFlow(EmailAutomatorException):
    """Invalid email flow configuration"""

    pass


class TemplateNotFound(EmailAutomatorException):
    """Email template not found"""

    pass


class RecipientNotFound(EmailAutomatorException):
    """Recipient not found"""

    pass
