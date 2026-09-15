from typing import Annotated, ClassVar, override

from fastapi import Depends
from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.operations import _IndexKeyHint

# from app.config import logger
from app.schemas import AuditEventModel
from saltbox_sdk.db.mongo.config import get_mongo
from saltbox_sdk.db.mongo.repository_time_series_base import TimeSeriesRepository
from saltbox_sdk.db.mongo.schemas_base import TimeSeriesConfig


class AuditRepository(TimeSeriesRepository[AuditEventModel]):
    class Meta:
        collection_name = 'audit_events'
        auto_now_add_fields: ClassVar[list[str]] = ['created']
        auto_now_fields: ClassVar[list[str]] = ['modified']
        collection_index_to_keys: ClassVar[dict[str, _IndexKeyHint]] = {
            'created_event_type_status_subject_id': [
                ('created', ASCENDING),
                ('resource_type', ASCENDING),
                ('status', ASCENDING),
                ('subject_id', ASCENDING),
            ],
            'created_action': [
                ('created', ASCENDING),
                ('action', ASCENDING),
            ],
            'created_subject_id': [
                ('created', ASCENDING),
                ('subject_id', ASCENDING),
            ],
            'created_resource_id': [
                ('created', ASCENDING),
                ('resource_id', ASCENDING),
            ],
            'created_correlation_id': [
                ('created', ASCENDING),
                ('correlation_id', ASCENDING),
            ],
            'created_subject_name': [
                ('created', ASCENDING),
                ('subject_name', ASCENDING),
            ],
        }
        timeseries: ClassVar[TimeSeriesConfig] = {
            'timeField': 'created',
            'metaField': 'source_service',
            'granularity': 'minutes',
        }
        expire_after_seconds: ClassVar[int] = 2592000  # 30 дней

    @override
    async def _post_create_collection(self) -> None:
        pass


def get_audit_repository(db: Annotated[AsyncDatabase, Depends(get_mongo)]) -> AuditRepository:
    return AuditRepository(database=db)
