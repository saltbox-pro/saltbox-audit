from typing import Annotated

from fastapi import Depends

from app.repository import AuditRepository, get_audit_repository
from app.schemas import AuditEventCreateSchema, AuditEventModel
from saltbox_sdk.serivces.mongo_base_service import MongoTimeseriesBaseService


class AuditService(MongoTimeseriesBaseService[AuditRepository, AuditEventModel, AuditEventCreateSchema]):
    pass


def get_audit_service(
    repo: Annotated[AuditRepository, Depends(get_audit_repository)],
) -> AuditService:
    return AuditService(repo)
