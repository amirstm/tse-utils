"""
This module uses httpx to fetch data asynchronously \
from the TSETMC website. 
"""
import httpx
from bs4 import BeautifulSoup
from tse_utils.tse_client.models import (
    TseClientInstrumentIdentitification,
    TseClientScrapeException
)


class TseClientScraper():
    """
    This class fetches data from tsetmc client.
    """
    base_address: str = "http://service.tsetmc.com/WebService/TseClient.asmx"

    def __init__(self):
        self.__client = httpx.AsyncClient(headers={
            "Host": "service.tsetmc.com",
            "SOAPAction": "http://tsetmc.com/Instrument",
            "accept": "text/xml",
            "Content-type": "text/xml"
        }, base_url=TseClientScraper.base_address)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__client.aclose()

    async def __get_instruments_list_raw(
            self,
            timeout: int = 3
    ) -> str:
        """Gets instruments list raw"""
        xml_data = """\
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Instrument xmlns="http://tsetmc.com/">
            <UserName>string</UserName>
            <Password>string</Password>
            <Flow>unsignedByte</Flow>
        </Instrument>
    </soap:Body>
</soap:Envelope>
"""
        http_content = xml_data.encode(encoding='UTF-8')
        req = await self.__client.post(
            self.base_address,
            content=http_content,
            timeout=timeout
        )
        if req.status_code != 200:
            raise TseClientScrapeException(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return req.text

    async def get_instruments_list(
            self,
            timeout: int = 3
    ) -> tuple[
        list[TseClientInstrumentIdentitification],
        list[TseClientInstrumentIdentitification]
    ]:
        """Get and process instruments list"""
        raw = await self.__get_instruments_list_raw(timeout=timeout)
        element = BeautifulSoup(raw, features="xml").findChild(
            "InstrumentResult").text
        processed = [TseClientInstrumentIdentitification(
            x.split(",")) for x in element.split(";")]
        return [
            x
            for x in processed
            if not x.is_index
        ], [
            x
            for x in processed
            if x.is_index
        ]
