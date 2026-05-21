import httpx

from app.config import Settings, logger

settings = Settings()


class HttpxClientSingletonFactory:
    _instance: httpx.AsyncClient | None = None

    @classmethod
    def get_instance(cls) -> httpx.AsyncClient:
        """Get a singleton instance of httpx.AsyncClient."""
        if cls._instance is None:
            auth = None
            if settings.app.basic_auth_username != '' and settings.app.basic_auth_password != '':
                auth = httpx.BasicAuth(settings.app.basic_auth_username, settings.app.basic_auth_password)
            timeout = httpx.Timeout(
                connect=settings.app.httpx_connect_timeout,
                read=settings.app.httpx_read_timeout,
                write=settings.app.httpx_write_timeout,
                pool=settings.app.httpx_pool_timeout,
            )
            limits = httpx.Limits(
                max_connections=settings.app.httpx_max_connections,
                max_keepalive_connections=settings.app.httpx_max_keepalive,
                keepalive_expiry=settings.app.httpx_keepalive_expiry,
            )
            cls._instance = httpx.AsyncClient(auth=auth, timeout=timeout, limits=limits)
            logger.debug('HTTPX AsyncClient initialized.')
        else:
            logger.debug('Using existing HTTPX AsyncClient instance.')
        return cls._instance
