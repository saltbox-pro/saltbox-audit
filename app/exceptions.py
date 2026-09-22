from fastapi import status

from saltbox_sdk.exceptions import SaltBoxBaseException


class AuditException(SaltBoxBaseException):
    """Base class for all audit-related exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = 'An unexpected error occurred in the audit service.'


class AuditAfterBeforeException(AuditException):
    """Exception raised when both after and before cursors are used together."""

    status_code = status.HTTP_400_BAD_REQUEST
    detail: str = 'Invalid cursor: `after` and `before` cannot be used together.'
