from fastapi import status

from saltbox_sdk.exceptions import SaltBoxBaseException


class AuditException(SaltBoxBaseException):
    """Base class for all audit-related exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = 'An unexpected error occurred in the audit service.'
