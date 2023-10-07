"""
This module holds tse client modules.
"""
from dataclasses import dataclass
from datetime import date
from tse_utils.models import instrument


@dataclass
class TseClientInstrumentIdentitification(instrument.InstrumentIdentification):
    """Instrument Identification from TseClient"""
    last_change_date: date = None
    is_index: bool = None
    market_code: int = None
    sector_code: int = None
    sub_sector_code: int = None
    type_id: int = None

    def __init__(self, tseclient_raw_data):
        instrument.InstrumentIdentification.__init__(
            self=self,
            tsetmc_code=tseclient_raw_data[0],
            isin=tseclient_raw_data[1],
            ticker=tseclient_raw_data[5],
            name_persian=tseclient_raw_data[6],
            name_english=tseclient_raw_data[3]
        )
        self.type_id = int(tseclient_raw_data[17])
        sector_code = str(tseclient_raw_data[15]).replace(" ", "")
        if sector_code.isdigit():
            self.sector_code = int(sector_code)
            self.sub_sector_code = int(tseclient_raw_data[16])
            self.is_index = False
        else:
            self.is_index = True
        self.market_code = int(tseclient_raw_data[9])
        last_change_date_raw = int(tseclient_raw_data[8])
        self.last_change_date = date(
            year=last_change_date_raw//10000,
            month=last_change_date_raw//100 % 100,
            day=last_change_date_raw % 100
        )


class TseClientScrapeException(Exception):
    """Tse client bad response status error"""

    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.get('status_code')
        super().__init__(*args)
