from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.config import logger
from app.schemas import AuditEventModel
from app.service import AuditService, get_audit_service
from saltbox_sdk.db.schemas_base import CursoredTimeseriesResponse
from saltbox_sdk.discovery_client.schemas import GatewayEndpointConfig

router = APIRouter(prefix='/events', tags=['Audit Events'])


@router.get(
    '',
    operation_id='audit_events_list',
    openapi_extra=GatewayEndpointConfig(
        policy='public',
        action='list',
        cache_ttl=0,
    ).model_dump(by_alias=True),
)
async def list_audit_events(
    response: Response,
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
    time_from: str | None = None,
    time_to: str | None = None,
) -> CursoredTimeseriesResponse[AuditEventModel]:
    # TODO: not implemented yet, just return empty list
    result = await audit_service.get_list_in_range_paginated(time_from=time_from, time_to=time_to)
    response.headers['X-Next-Cursor'] = str(result.next_cursor) if result.next_cursor else ''
    logger.debug(f'Events[0]: {result.data[0] if result.data else "No events"}, Next cursor: {result.next_cursor}')
    return result
