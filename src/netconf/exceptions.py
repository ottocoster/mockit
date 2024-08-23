class UnexpectedRequestError(Exception):
    """Indicates that a request has been received that has no predefined response."""


class RequestError(Exception):
    """Indicates that an error occurred when processing the request."""
