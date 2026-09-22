from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends

from app.schemas import AuditEventActionsSchema, AuditEventListBody, AuditEventModel
from app.service import AuditService, get_audit_service
from saltbox_sdk.db.mongo.schemas_base import CursoredTimeseriesResponse
from saltbox_sdk.discovery_client.schemas import GatewayEndpointConfig
from saltbox_sdk.event_bus.schemas import AuditCategory, AuditResourceType, AuditSeverity, AuditStatus, AuditSubjectType

router = APIRouter(prefix='/events', tags=['Audit Events'])


@router.post(
    '/list',
    operation_id='audit_events_list',
    openapi_extra=GatewayEndpointConfig(
        policy='public',
        action='list',
        cache_ttl=0,
    ).model_dump(by_alias=True),
)
async def list_audit_events(
    body: Annotated[AuditEventListBody, Body()],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
) -> CursoredTimeseriesResponse[AuditEventModel]:
    result = await audit_service.get_list_in_range_paginated(
        query=body.query,
        after=body.after,
        before=body.before,
        limit=body.limit,
        sort=body.sort,
    )
    return result


@router.get(
    '/schema',
    operation_id='audit_events_filter_schema',
    openapi_extra=GatewayEndpointConfig(
        policy='public',
        action=AuditEventActionsSchema.GET_SCHEMA,
    ).model_dump(by_alias=True),
)
async def events_filter_schema() -> list[dict[str, Any]]:
    select_operators = [
        {'name': '=', 'value': '=', 'label': '='},
        {'name': '!=', 'value': '!=', 'label': '!='},
    ]
    text_operators = [
        {'name': '=', 'value': '=', 'label': '='},
        {'name': '!=', 'value': '!=', 'label': '!='},
    ]
    datetime_operators = [
        {'name': '<', 'value': '<', 'label': '<'},
        {'name': '<=', 'value': '<=', 'label': '<='},
        {'name': '>', 'value': '>', 'label': '>'},
        {'name': '>=', 'value': '>=', 'label': '>='},
    ]
    allowed_filter_fields: list[dict[str, Any]] = [
        # Severity filter
        {
            'name': 'severity',
            'label': 'Severity',
            'valueEditorType': 'select',
            'values': [{'name': severity.value, 'label': severity.value} for severity in AuditSeverity],
            'defaultValue': AuditSeverity.INFO.value,
            'operators': select_operators,
        },
        # Category filter
        {
            'name': 'category',
            'label': 'Category',
            'valueEditorType': 'select',
            'values': [{'name': category.value, 'label': category.value} for category in AuditCategory],
            'defaultValue': AuditCategory.SYSTEM.value,
            'operators': select_operators,
        },
        # Status filter
        {
            'name': 'status',
            'label': 'Status',
            'valueEditorType': 'select',
            'values': [{'name': status.value, 'label': status.value} for status in AuditStatus],
            'defaultValue': AuditStatus.SUCCESS.value,
            'operators': select_operators,
        },
        # Action filter
        {
            'name': 'action',
            'label': 'Action',
            'operators': text_operators,
        },
        # Subject name filter
        # Subject name filter
        {
            'name': 'subject_name',
            'label': 'Subject Name',
            'valueEditorType': 'text',
            'operators': text_operators,
        },
        # Subject type filter
        {
            'name': 'subject_type',
            'label': 'Subject Type',
            'valueEditorType': 'select',
            'values': [{'name': subject_type.value, 'label': subject_type.value} for subject_type in AuditSubjectType],
            'defaultValue': AuditSubjectType.USER.value,
            'operators': select_operators,
        },
        # Resource type filter
        {
            'name': 'resource_type',
            'label': 'Resource Type',
            'valueEditorType': 'select',
            'values': [
                {'name': resource_type.value, 'label': resource_type.value} for resource_type in AuditResourceType
            ],
            'operators': select_operators,
        },
        # Source service filter
        {
            'name': 'source_service',
            'label': 'Source Service',
            'valueEditorType': 'text',
            'operators': text_operators,
        },
        # Correlation ID filter
        {
            'name': 'correlation_id',
            'label': 'Correlation ID',
            'valueEditorType': 'text',
            'operators': [
                {'name': '=', 'value': '=', 'label': '='},
            ],
        },
        # SIEM sent filter
        {
            'name': 'siem_sent',
            'label': 'SIEM Sent',
            'valueEditorType': 'checkbox',
            'defaultValue': False,
            'operators': [
                {'name': '=', 'value': '=', 'label': '='},
            ],
        },
        # Created filter
        {
            'name': 'created',
            'label': 'Created',
            'valueEditorType': 'datetime-local',
            'inputType': 'datetime-local',
            'dataType': 'timestamp with time zone',
            'operators': datetime_operators,
        },
    ]

    return allowed_filter_fields
