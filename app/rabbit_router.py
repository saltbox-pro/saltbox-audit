import logging
from typing import Annotated

from fastapi import Depends
from faststream.rabbit.fastapi import Logger, RabbitMessage, RabbitRouter

from app.config import Settings
from app.schemas import AuditEventCreateSchema
from app.service import AuditService, get_audit_service

settings = Settings()
fs_router = RabbitRouter(settings.rabbitmq.url, log_level=logging.DEBUG)


@fs_router.subscriber('audit_events')
async def audit_msg_received(
    message: AuditEventCreateSchema,
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
    msg: RabbitMessage,
    fs_logger: Logger,
) -> None:
    fs_logger.warning(f'Received audit message:{message.event_id}')
    fs_logger.info(f'Message:\n{message}')
    try:
        await audit_service.create(message)
        await msg.ack()
    except Exception as e:
        fs_logger.error(f'Error processing audit message: {e}')
    fs_logger.warning(f'Finished processing audit message: {message.correlation_id} - {message.event_id}')
