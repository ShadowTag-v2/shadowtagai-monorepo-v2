"""Custom exceptions for the application"""


class EmailAutomatorException(Exception):
    """Base exception for email automator"""



class EmailProviderError(EmailAutomatorException):
    """Email provider related errors"""



class RateLimitExceeded(EmailAutomatorException):
    """Rate limit exceeded"""



class InvalidEmailFlow(EmailAutomatorException):
    """Invalid email flow configuration"""



class TemplateNotFound(EmailAutomatorException):
    """Email template not found"""



class RecipientNotFound(EmailAutomatorException):
    """Recipient not found"""

