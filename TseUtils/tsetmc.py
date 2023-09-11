import asyncio, httpx, json
from TseUtils.exceptions import MyProjectError
from dataclasses import dataclass

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

    async def get_instrument_identity_raw(self, tsetmc_code: str, timeout: int = 3):
        r = await self.__client.get(f"api/Instrument/GetInstrumentIdentity/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)

    async def get_instrument_identity(self, tsetmc_code: str, timeout: int = 3):
        raw = await self.get_instrument_identity_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return InstrumentIdentification(tsetmc_raw_data=raw["instrumentIdentity"])

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__client.aclose()

@dataclass
class InstrumentIdentification:
    isin: str = None
    tsetmc_code: str = None
    ticker: str = None
    name_persian: str = None
    name_english: str = None
    market_code: int = None
    market_title: str = None
    sector_code: int = None
    sector_title: str = None
    sub_sector_code: int = None
    sub_sector_title: str = None
    type_id: int = None

    def __init__(self, tsetmc_raw_data):
        self.isin = tsetmc_raw_data["instrumentID"]
        self.name_english = tsetmc_raw_data["lVal18"]
        self.name_persian = tsetmc_raw_data["lVal30"]
        self.ticker = tsetmc_raw_data["lVal18AFC"]
        self.market_title = tsetmc_raw_data["cgrValCotTitle"]
        self.market_code = tsetmc_raw_data["cComVal"]
        self.sector_code = int(tsetmc_raw_data["sector"]["cSecVal"].replace(" ", ""))
        self.sector_title = tsetmc_raw_data["sector"]["lSecVal"]
        self.sub_sector_code = tsetmc_raw_data["subSector"]["cSoSecVal"]
        self.sub_sector_title = tsetmc_raw_data["subSector"]["lSoSecVal"]
        self.type_id = int(tsetmc_raw_data["yVal"])

    def __str__(self):
        return f"{self.ticker} [{self.isin}]"

class TsetmcScrapeError(MyProjectError):
   """Tsetmc bad response status error."""
   def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.status_code = kwargs.get('status_code')