import httpx

from src.utils.exceptions import RequestDataException

class Request:
    def __init__(self, url: str, headers: dict = {}, params: str | dict = {}):
        self.url = url
        self.headers = headers 
        self.params = params

    async def get(self, **kwargs) -> httpx.Response:
        if isinstance(self.params, str):
            raise RequestDataException("Method `GET` not accept argument `params` with type `str`!")
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            response = await client.get(self.url, params=self.params, headers=self.headers, **kwargs)
            return response
    
    async def post(self, timeout: int = 600) -> httpx.Response:
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            if isinstance(self.params, str):
                request_params = {
                    "url": self.url,
                    "data": self.params,
                    "headers": self.headers
                }
            else:
                request_params = {
                    "url": self.url,
                    "json": self.params,
                    "headers": self.headers
                }
            response = await client.post(timeout=timeout, **request_params)
            return response