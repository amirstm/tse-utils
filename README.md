# TSE-UTILS

TSE-UTILS is a Python library designed to facilitate data retrieval of the Tehran Stock Exchange (TSE) market. It includes a versatile set of tools, including a module for scraping data from the official [TSETMC](http://www.tsetmc.com) website and the TSE Client API. Whether you are an investor, data analyst, or researcher, TSE-UTILS offers a range of features to help you access and work with TSE market data efficiently.

## Features

- **Data Retrieval**: Easily fetch data from the Tehran Stock Exchange.
- **Web Scraping**: Access real-time market data from [TSETMC](http://www.tsetmc.com).
- **Customization**: Adapt the library to your specific research or investment needs.

## Installation

Install TSE-UTILS using pip:

   ```bash
   pip install tse-utils
   ```
## Examples

1. **Get Instruments**: Get the list of instruments and indices for TSE Client:

    ```bash
    from tse_utils.tse_client import TseClientScraper

    async with TseClientScraper() as tse_client:
        instruments, indices = await tse_client.get_instruments_list()
    ```

2. **Search for Instruments**: Search for instruments on TSETMC:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        search_result = await tsetmc.get_instrument_search(search_value="فولاد")
    ```

3. **Get Instrument Identity**: Get an instrument's identity using its tsetmc code:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        identity = await tsetmc.get_instrument_identity(tsetmc_code="46348559193224090")
    ```

4. **Get Current Instrument Stats**: Get an instrument's current stats, consisting of prices and volumes:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        stats = await tsetmc.get_closing_price_info(tsetmc_code="46348559193224090")
    ```

5. **Get Instrument Home Page Data**: Get an instrument's home page data, consisting of daily, weekly, and anual price ranges and brief identity info:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        homepage_data = await tsetmc.get_instrument_info(tsetmc_code="46348559193224090")
    ```
