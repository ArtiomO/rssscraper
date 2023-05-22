import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from app.clients.decorators import retry


class HttpClientConnectionError(Exception):
    pass


class HttpClient:
    """Http client."""

    @retry(HttpClientConnectionError)
    async def request(self, url: str, method: str) -> tuple(int, dict):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method=method, url=url) as resp:
                    resp_body = await resp.text()
                    return resp.status, resp_body
        except ClientConnectorError:
            raise HttpClientConnectionError


http_client = HttpClient()
