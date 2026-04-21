from app.repository import get_audit_repository
from saltbox_sdk.db.mongo.config import get_mongo_db


async def init_mongo_db() -> None:
    """Initialize MongoDB collections"""

    database = get_mongo_db()
    audit_repo = get_audit_repository(database)
    await audit_repo.create_collection()
