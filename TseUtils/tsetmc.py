import asyncio, httpx, json

class TsetmcScraper():
    """
    This class fetches data from tsetmc.com, the official website for Tehran Stock Exchange market data.
    """
    def __init__(self, tsetmc_domain: str = "cdn.tsetmc.com"):
        self.tsetmc_domain = tsetmc_domain
        self.__client = httpx.AsyncClient(headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "accept": "application/json, text/plain, */*"
        }, base_url=f"http://{tsetmc_domain}/")

    async def get_instrument_identity(self, tsetmc_code: str, timeout: int = 3):
        r = await self.__client.get(f"api/Instrument/GetInstrumentIdentity/{tsetmc_code}", timeout=timeout)
        return json.loads(r.text)
