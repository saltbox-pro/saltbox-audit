from abc import ABC, abstractmethod
from typing import Any

from app.schemas import AuditEventModel


class SIEMAdapter(ABC):
    @abstractmethod
    def transform(self, event: AuditEventModel) -> dict[str, Any]: ...


class MaxPatrolAdapter(SIEMAdapter):
    def transform(self, event: AuditEventModel) -> dict[str, Any]:
        return {
            'event_id': event.event_id,
            'event_time': event.created.isoformat(),
            'severity': event.severity.value.upper(),
            'event_type': f'{event.category}.{event.action}',
            'status': event.status.value,
            'user': event.subject_name or event.subject_id,
            'ip': event.source_ip or '0.0.0.0',  # noqa: S104
            'service': event.source_service,
            'resource': event.resource_path or event.resource_id or '',
            'payload': event.details,
        }


class WazuhAdapter(SIEMAdapter):
    def transform(self, event: AuditEventModel) -> dict[str, Any]:
        return {
            'timestamp': event.created.isoformat(),
            'event.module': event.source_service,
            'event.action': event.action,
            'event.category': [event.category],
            'event.severity': event.severity.value,
            'user.name': event.subject_name,
            'user.id': event.subject_id,
            'source.ip': event.source_ip,
            'data': event.details,
            'message': f'[{event.status.value}] {event.action} on {event.resource_path or event.resource_type}',
        }


class MozDefAdapter(SIEMAdapter):
    def transform(self, event: AuditEventModel) -> dict[str, Any]:
        sev_map = {'info': 0, 'low': 1, 'medium': 3, 'high': 7, 'critical': 10}
        return {
            'timestamp': int(event.created.timestamp() * 1000),
            'summary': f'{event.category}.{event.action} [{event.status.value}]',
            'category': event.category,
            'severity': sev_map.get(event.severity.value, 1),
            'tags': [event.source_service, event.action, event.status.value],
            'hostname': event.source_service,
            'details': event.details,
            'actors': [{'username': event.subject_name, 'userid': event.subject_id}],
            'ip': event.source_ip,
        }
