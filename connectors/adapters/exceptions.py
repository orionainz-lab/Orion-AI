"""
Connector Exceptions

Custom exceptions for adapter operations.
"""


class ConnectorError(Exception):
    """Base exception for all connector errors"""
    
    def __init__(
        self,
        message: str,
        code: str = "connector_error",
        details: dict = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(ConnectorError):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="auth_expired"
        )


class RateLimitError(ConnectorError):
    """Rate limit exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = None
    ):
        super().__init__(
            message=message,
            code="rate_limit",
            details={"retry_after": retry_after}
        )


class ValidationError(ConnectorError):
    """Data validation failed"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="validation_error",
            details={"field": field}
        )


class APIError(ConnectorError):
    """External API error"""
    
    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_body: str = None
    ):
        super().__init__(
            message=message,
            code="api_error",
            details={
                "status_code": status_code,
                "response": response_body
            }
        )
