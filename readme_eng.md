# Econ DataReader

**Econ DataReader** is a Python library designed to easily fetch economic and financial data from various sources such as the Bank of Korea, FRED (Federal Reserve Economic Data), domestic and international financial market data, and cryptocurrency prices. This tool simplifies data collection and can be seamlessly integrated into data science workflows.

## Key Features

- Fetch economic data from various sources, including:
    - Trad-Fi market data (stocks, bonds, etc.)
    - Cryptocurrency: Upbit spot prices, Binance spot/futures prices
    - FRED
    - Bank of Korea

## Installation

You can easily install econ-datareader using pip.

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
  - Data Type: Choose one from `KOREA_STOCK`, `GLOBAL_FINANCE`, `CRYPTO_SPOT_BINANCE`, `CRYPTO_FUTURES_BINANCE`, `CRYPTO_SPOT_UPBIT`
  - Tickers: Input in the format `['Ticker1', 'Ticker2']`
  - Time Interval: Input as a string such as `1m`, `1h`, `1d`, `1M`
  - Start Time: Input in the format `YYYYMMddHHmm` (as an `int`)
  - End Time: Same format as Start Time

You can access specific data as shown below. For example, to retrieve the ETHUSDT data from the above example:
```python
eth_data = data['ETHUSDT']
```
For `KOREA_STOCK`, intraday data can only be downloaded up to 7 business days prior to the execution date. For `GLOBAL_FINANCE`, minute-level intraday data can be downloaded for up to 30 days, and hourly intraday data for up to 730 days.

### FRED
```python
from econdatareader.fred import FredDownloader

downloader = FredDownloader(api_key='your_api_key')
data = downloader.download_data(['Code1', 'Code2'], '2011-01-01', '2024-08-01')
```
To download FRED data, you need to obtain an API_KEY from FRED. You can register and get an API_KEY at the link below:
  - https://fred.stlouisfed.org/

The arguments for the `download_data` method are as follows:
  - Data ID: Input as `['Code1', 'Code2']`
  - Start Date: Input in the format `YYYY-mm-dd` (as a `str`)
  - End Date: Same format as Start Date

You can search for the unique ID of the data on FRED by using keywords. For example, the daily Dollar Index ID is `DTWEXBGS`.

To retrieve specific data, for example, the Dollar Index from the above example:
```python
dollar_index_data = data['DTWEXBGS']
```

### Bank of Korea (BOK)
```python
from econdatareader.bok import BokDownloader

downloader = BokDownloader(api_key='your_api_key')
data = downloader.download_data([('StatCode1', 'A', '2013', '2024', 'ItemCode1'), 
('StatCode2', 'Q', '2015Q1', '2024Q2', 'ItemCode2'),
('StatCode3', 'M', '201501', '202407' 'ItemCode3'),
('Statcode4', 'D', '20110101', '20240101', 'ItemCode4')])
```
To download data from the Bank of Korea Economic Statistics System, you need to register and obtain an API_KEY from the link below:
 - https://ecos.bok.or.kr/api/#/

The arguments for the `download_data` method are as follows:
  - Input in the format `(Data ID, Time Interval, Start Date, End Date, Sub Data ID)` (as shown in the code example above)
  - Time Interval: Choose one from `D`, `M`, `Q`, `A`
  - Start Date and End Date:
    - For `D`, use the format `YYYYMMDD`
    - For `M`, use the format `YYYYMM`
    - For `Q`, use the format `YYYYQd` (where `d=1,2,3,4`)
    - For `A`, use the format `YYYY`
 - Data ID and Sub Data ID can be found on the Bank of Korea Economic Statistics System.

To retrieve specific data, for example, the data for `Statcode1` from the above example:
```python
stat1_data = data['StatCode1-ItemCode1'] 
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions, please contact `wydanielchoi@gmail.com`.