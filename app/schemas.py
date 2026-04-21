from pydantic import ConfigDict

from saltbox_sdk.db.mongo.schemas_base import IDMixin
from saltbox_sdk.db.schemas_base import CreatedModifiedMixin
from saltbox_sdk.event_bus.schemas import (
    AuditCategory,
    AuditEventSchema,
    AuditResourceType,
    AuditSeverity,
    AuditStatus,
    AuditSubjectType,
)


class AuditEventCreateSchema(AuditEventSchema):
    pass


class AuditEventModel(IDMixin, CreatedModifiedMixin, AuditEventCreateSchema):
    model_config = ConfigDict(
        frozen=False,
        json_schema_extra={
            'examples': [
                {
                    'event_id': '123e4567-e89b-12d3-a456-426614174000',
                    'created': '2026-04-14T10:00:00Z',
                    'modified': '2026-04-14T10:00:00Z',
                    'severity': AuditSeverity.INFO,
                    'category': AuditCategory.DATA_ACCESS,
                    'action': 'list',
                    'status': AuditStatus.SUCCESS,
                    'subject_id': '26b9a3e6-2e80-40c7-8f84-a993a1282169',
                    'subject_name': 'Ivan Ivanov',
                    'subject_roles': ['test_common'],
                    'subject_type': AuditSubjectType.USER,
                    'resource_type': AuditResourceType.COLLECTION,
                    'resource_id': None,
                    'resource_path': '/collections',
                    'source_ip': '192.168.10.42',
                    'source_service': 'core',
                    'correlation_id': 'd4c3b2a1-5678-90ab-cdef-1234567890ab',
                    'details': {'policy_id': 'core.collections.list', 'response_time_ms': 120},
                    'siem_sent': False,
                }
            ]
        },
    )
