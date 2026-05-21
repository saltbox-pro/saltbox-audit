# Salt.Box Audit

Микросервис централизованного сбора, хранения и предоставления событий аудита платформы SaltBox. Обеспечивает неизменяемый журнал действий пользователей и сервисов.

---

## Архитектура

```
[Любой сервис] → RabbitMQ (audit_events) → saltbox-audit → MongoDB Time Series (audit_events)
                                                            ↑
                                              HTTP GET /events (Gateway / UI)
```

- **Intake**: события публикуются в очередь `audit_events` в формате `AuditEventSchema`.
- **Storage**: MongoDB Time Series коллекция, отдельный инстанс `mongodb-audit` (Replica Set).
- **Query**: REST API с cursor-based пагинацией.
- **Export**: адаптеры для SIEM (MaxPatrol, Wazuh, MozDef) через `SIEMAdapter`.


## Схема события (`AuditEventSchema`)

| Поле | Тип | Описание |
|---|---|---|
| `event_id` | `str` (UUID) | Уникальный ID события |
| `severity` | `AuditSeverity` | `info` / `low` / `medium` / `high` / `critical` |
| `category` | `AuditCategory` | `authentication`, `authorization`, `configuration`, `data_access`, `system`, `lifecycle` |
| `action` | `str` | Действие: `login`, `delete_record`, `apply_state` и т.д. |
| `status` | `AuditStatus` | `success` / `failure` / `denied` / `blocked` |
| `subject_id` | `str \| None` | ID субъекта (пользователь / сервис) |
| `subject_name` | `str \| None` | Имя субъекта |
| `subject_roles` | `list[str]` | Роли субъекта |
| `subject_type` | `AuditSubjectType` | `user` / `service` / `system` |
| `resource_type` | `AuditResourceType` | Тип ресурса: `collection`, `task`, `job` и др. |
| `resource_id` | `str \| None` | ID ресурса |
| `resource_path` | `str \| None` | Путь ресурса (API endpoint, file path) |
| `source_ip` | `str \| None` | IP источника |
| `source_service` | `str` | Сервис-источник (`core`, `gateway` и т.д.) |
| `correlation_id` | `str \| None` | ID для связи событий между сервисами |
| `details` | `dict` | Дополнительные данные |
| `siem_sent` | `bool` | Признак отправки в SIEM |

При сохранении автоматически добавляются поля `_id`, `created`, `modified`.

## Хранение (MongoDB Time Series)

| Параметр | Значение |
|---|---|
| Коллекция | `audit_events` |
| `timeField` | `created` (BSON Date) |
| `metaField` | `source_service` |
| `granularity` | `minutes` |
| TTL | 30 дней (`expireAfterSeconds: 2592000`) |
| Индекс | `created + resource_type + status + subject_id` |

TS-коллекция **append-only**: обновление и удаление отдельных документов не поддерживается.

## Публикация события из другого сервиса

```python
from saltbox_sdk.event_bus.schemas import AuditEventSchema, AuditCategory, AuditStatus, AuditSeverity

event = AuditEventSchema(
    severity=AuditSeverity.INFO,
    category=AuditCategory.DATA_ACCESS,
    action="list",
    status=AuditStatus.SUCCESS,
    source_service="core",
    subject_id="user-uuid",
    resource_type="collection",
    resource_path="/api/collections",
)
# Публикация в RabbitMQ очередь 'audit_events'
await broker.publish(event, queue="audit_events")
```
