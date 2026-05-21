from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import Settings, logger
from app.db import init_mongo_db
from app.rabbit_router import fs_router
from app.router import router

# from app.serve import broker
from app.utils.httpx_client import HttpxClientSingletonFactory
from saltbox_sdk.config.discovery_config import DISCOVERY_SETTINGS
from saltbox_sdk.discovery_client.client import DiscoveryClient
from saltbox_sdk.discovery_client.schemas import HealthCheckResponse
from saltbox_sdk.exceptions import SaltBoxBaseException
from saltbox_sdk.fastapi_utils.custom_openapi import custom_openapi, patch_swagger_config
from saltbox_sdk.fastapi_utils.exception_handlers import custom_http_handler
from saltbox_sdk.fastapi_utils.promethes_metrics.exporter import PrometheusExporter

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    logger.debug('Starting application lifespan...')
    await init_mongo_db()
    discovery_client = DiscoveryClient(
        openapi_schema=app.openapi(),
        httpx_client=HttpxClientSingletonFactory.get_instance(),
    )
    await discovery_client.register()

    yield


app_config: dict[str, Any] = {
    'title': settings.app.app_name,
    'lifespan': lifespan,
    'version': __version__,
    'description': settings.app.app_desc,
    'root_path': settings.app.base_url_root_path,
    'healthcheck_path': '/discovery/health',
    # 'docs_url': '/docs', # or None to disable
    # 'openapi_url': '/openapi.json', # or None to disable
}

app_config = patch_swagger_config(app_config)


class _App(FastAPI):
    def openapi(self) -> dict[str, Any]:
        return custom_openapi(self, app_config, servers=[{'url': settings.app.base_url_root_path}])


app = _App(**app_config)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_exception_handler(SaltBoxBaseException, custom_http_handler)
PrometheusExporter(app).expose_metrics()


@app.get('/discovery/health')
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    return HealthCheckResponse(
        status='ok',
        message=f'Instance of {DISCOVERY_SETTINGS.service_name} is running',
    )


app.include_router(router=router)
app.include_router(router=fs_router)
