# Econ DataReader

<div align="right">

[![Pypi Package Ver.](https://img.shields.io/pypi/v/econ-datareader.svg)](https://pypi.org/project/econ-datareader/)
[![License](https://img.shields.io/pypi/l/ansicolortags.svg)](https://img.shields.io/pypi/l/ansicolortags.svg)

<div align="left">

**Econ DataReader** is a Python library designed to easily fetch economic and financial data from various sources, including the Bank of Korea, FRED (Federal Reserve Economic Data), domestic and international financial market data, and cryptocurrency prices. This tool simplifies data collection and can be seamlessly integrated into data science workflows.

## Key Features

- Fetch economic data from various sources such as:
    - Trad-Fi market data (stocks, bonds, etc.)
    - Cryptocurrencies: Upbit spot prices, Binance spot/futures prices
    - FRED
    - Bank of Korea (BOK)

## Installation

You can easily install econ-datareader via pip.

```bash
pip install econ-datareader
```

## Usage
Here are some examples of how to use econ-datareader.

### Trad-Fi and Cryptocurrency
```python
from econdatareader.finance import FinanceDownloader

downloader = FinanceDownloader()
data = downloader.download_data('CRYPTO_SPOT_BINANCE', ['BTCUSDT', 'ETHUSDT'], '1m', 202407240000, 202408050000)
```
The arguments for the `download_data` method are as follows:
  - Data Type: Choose from `KOREA_STOCK`, `GLOBAL_FINANCE`, `CRYPTO_SPOT_BINANCE`, `CRYPTO_FUTURES_BINANCE`, `CRYPTO_SPOT_UPBIT`
  - Ticker: Enter as `['Ticker1', 'Ticker2']`
  - Time Interval: Enter as a string like `1m`, `1h`, `1d`, `1M`
  - Start Time: Enter as `YYYYMMddHHmm` format (`int` type)
  - End Time: Same format as Start Time

To retrieve data, you can use the following. For instance, to get ETHUSDT data from the example above:
```python
eth_data = data['ETHUSDT']
```
For `KOREA_STOCK`, intraday data is only available for up to 7 business days from the current date. For `GLOBAL_FINANCE`, minute-level intraday data is available for up to 30 days, while hourly data is available for up to 730 days.

### FRED
```python
from econdatareader.fred import FredDownloader

downloader = FredDownloader(api_key='your_api_key')
id_table = downloader.search_series_by_keyword('core consumer price index')
data = downloader.download_data(['Code1', 'Code2'], '2011-01-01', '2024-08-01')
```
To download FRED data, you need to obtain an API_KEY from FRED. You can sign up and get your API_KEY from the following link:
  - https://fred.stlouisfed.org/
  
The arguments for the `search_series_by_keyword` method are as follows:
  - keyword: Enter as a `str` type. For example, to find the id of the Core CPI, you might input `core consumer price index`.

The arguments for the `download_data` method are as follows:
  - Data IDs: Enter as `['Code1', 'Code2']`
  - Start Time: Enter as `YYYY-mm-dd` format (`str` type)
  - End Time: Same format as Start Time

Each data series has a unique ID that can be found through keyword search on FRED. For example, the daily US Dollar Index ID is `DTWEXBGS`.

To retrieve data, you can use the following. For instance, to get the Dollar Index data from the example above:
```python
dollar_index_data = data['DTWEXBGS']
```

### Bank of Korea (BOK)
```python
from econdatareader.bok import BokDownloader

downloader = BokDownloader(api_key='your_api_key')
id_table = downloader.search_stat_code_by_keyword('소비자물가')
data = downloader.download_data([('StatCode1', 'A', '2013', '2024', 'ItemCode1'), 
('StatCode2', 'Q', '2015Q1', '2024Q2', 'ItemCode2'),
('StatCode3', 'M', '201501', '202407' 'ItemCode3'),
('Statcode4', 'D', '20110101', '20240101', 'ItemCode4')])
```
To download data from the Bank of Korea's economic statistics system, you need to obtain an API_KEY. You can sign up and get your API_KEY from the following link:
 - https://ecos.bok.or.kr/api/#/

The arguments for the `search_stat_code_by_keyword` method are as follows:
  - keyword: Enter as a `str` type. For example, to find the STAT_CODE for the Consumer Price Index, you might input `소비자물가지수`.

The arguments for the `download_data` method are as follows:
  - `(Data ID, Time Interval, Start Time, End Time, Data Sub ID)` in the order shown above (refer to the code example)
  - Time Interval: Choose from `D`, `M`, `Q`, `A`
  - Start Time and End Time
    - For `D`, enter as `YYYYMMDD` format
    - For `M`, enter as `YYYYMM` format
    - For `Q`, enter as `YYYYQd` format (`d=1,2,3,4`)
    - For `A`, enter as `YYYY` format
 - Data ID and Data Sub ID can be referenced from the Bank of Korea's economic statistics system.

To retrieve data, you can use the following. For instance, to get the data for `Statcode1` from the example above:
```python
stat1_data = data['StatCode1-ItemCode1'] 
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions, please contact `wydanielchoi@gmail.com`.
