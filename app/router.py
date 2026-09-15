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
        time_from=body.time_from,
        time_to=body.time_to,
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
        # {'name': 'in', 'value': 'in', 'label': 'in'},
        # {'name': 'notIn', 'value': 'notIn', 'label': 'not in'},
    ]
    text_operators = [
        {'name': '=', 'value': '=', 'label': '='},
        {'name': '!=', 'value': '!=', 'label': '!='},
        {'name': 'beginsWith', 'value': 'beginsWith', 'label': 'begins with'},
        # {'name': 'endsWith', 'value': 'endsWith', 'label': 'ends with'},
        # {'name': 'contains', 'value': 'contains', 'label': 'contains'},
        # {'name': 'doesNotContain', 'value': 'doesNotContain', 'label': 'does not contain'},
        # {'name': 'doesNotBeginWith', 'value': 'doesNotBeginWith', 'label': 'does not begin with'},
        # {'name': 'doesNotEndWith', 'value': 'doesNotEndWith', 'label': 'does not end with'},
        # {'name': 'in', 'value': 'in', 'label': 'in'},
        # {'name': 'notIn', 'value': 'notIn', 'label': 'not in'},
        # {'name': 'null', 'value': 'null', 'label': 'is null'},
        # {'name': 'notNull', 'value': 'notNull', 'label': 'is not null'},
    ]
    allowed_filter_fields: list[dict[str, Any]] = [
        # Severity filter
        {
            'name': 'severity',
            'label': 'Severity',
            'valueEditorType': 'select',
            'values': [severity.value for severity in AuditSeverity],
            'defaultValue': AuditSeverity.INFO.value,
            'operators': select_operators,
        },
        # Category filter
        {
            'name': 'category',
            'label': 'Category',
            'valueEditorType': 'select',
            'values': [category.value for category in AuditCategory],
            'defaultValue': AuditCategory.SYSTEM.value,
            'operators': select_operators,
        },
        # Status filter
        {
            'name': 'status',
            'label': 'Status',
            'valueEditorType': 'select',
            'values': [status.value for status in AuditStatus],
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
            'values': [subject_type.value for subject_type in AuditSubjectType],
            'defaultValue': AuditSubjectType.USER.value,
            'operators': select_operators,
        },
        # Resource type filter
        {
            'name': 'resource_type',
            'label': 'Resource Type',
            'valueEditorType': 'select',
            'values': [resource_type.value for resource_type in AuditResourceType],
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
        },
    ]

    return allowed_filter_fields
