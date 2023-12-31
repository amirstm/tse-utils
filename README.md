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

6. **Get Instrument Client Type Data**: Get an instrument's client type data, consisting of trade shares for real and legal entities:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        client_type_data = await tsetmc.get_client_type(tsetmc_code="46348559193224090")
    ```

7. **Get Instrument Orderbook**: Get an instrument's latest orderbook:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        orderbook = await tsetmc.get_best_limits(tsetmc_code="46348559193224090")
    ```

8. **Get Historical Daily Prices**: Get an instrument's historical daily prices:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        historical = await tsetmc.get_closing_price_daily_list(tsetmc_code="46348559193224090")
    ```

9. **Get Historical Daily Client Type Data**: Get an instrument's historical client type data:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        historical = await tsetmc.get_client_type_daily_list(tsetmc_code="46348559193224090")
    ```

10. **Get Current Intraday Tick Trades**: Get an instrument's tick trade data within the last trading day:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        tick_trades = await tsetmc.get_trade_intraday_list(tsetmc_code="46348559193224090")
    ```

11. **Get Current Intraday Tick Trades**: Get an instrument's price adjustments, which happen after dividends and capital raises:

    ```bash
    from tse_utils.tsetmc import TsetmcScraper

    async with TsetmcScraper() as tsetmc:
        price_adjustments = await tsetmc.get_price_adjustment_list(tsetmc_code="46348559193224090")
    ```