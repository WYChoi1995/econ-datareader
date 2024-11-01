import aiohttp
import asyncio
import logging
import pandas as pd
import re
import nest_asyncio

from datetime import datetime

class FinanceDownloader(object):
    KOREA_STOCK_VALID_INTERVAL = ['minute', 'minute3', 'minute5', 'minute10', 'minute30', 'minute60', 'day', 'week', 'month']
    GLOBAL_FINANCE_DATA_VALID_INTERVAL = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']
    CRYPTO_BINANCE_VALID_INTERVAL = ['1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    CRYTPO_UPBIT_VALID_INTERVAL = ['1m', '3m', '5m', '10m', '15m', '30m', '60m', '240m', '1d', '1w', '1M']
    TIME_FACTORS = {'s': 1000, 'm': 60 * 1000, 'h': 3600 * 1000, 'd': 86400 * 1000, 'w': 604800 * 1000, 'M': 2592000 * 1000}
    GLOBAL_CANDLE_LIMITS = {'m': 7 * 24 * 60 * 60, 'h': 30 * 24 * 60 * 60, 'd': 365 * 24 * 60 * 60}
    AVAILABLE_DOWNLOAD_TYPE = ['KOREA_STOCK', 'GLOBAL_FINANCE', 'CRYPTO_SPOT_BINANCE', 'CRYPTO_FUTURES_BINANCE', 'CRYPTO_SPOT_UPBIT']

    def __init__(self):
        self.__binance_spot_uri = 'https://api.binance.com/api/v3/klines'
        self.__binance_futures_uri = 'https://fapi.binance.com/fapi/v1/klines'
        self.__naver_finance_uri = 'https://api.stock.naver.com/chart/domestic/item/'
        self.__yahoo_finance_uri = 'https://query1.finance.yahoo.com/v8/finance/chart/'
        self.__upbit_spot_uri = 'https://api.upbit.com/v1/candles/'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.__binance_rate_count = 0
        self.__upbit_rate_count_sec = 9
        self.__upbit_rate_count_min = 600

        nest_asyncio.apply()
    
    @staticmethod
    def __convert_interval_to_ms(interval: str):
        return int(interval[:-1]) * FinanceDownloader.TIME_FACTORS[interval[-1]]
    
    @staticmethod
    def __convert_interval_to_sec(interval: str):
        return int(interval[:-1]) * FinanceDownloader.GLOBAL_CANDLE_LIMITS[interval[-1]]

    @staticmethod
    def __convert_datetime_to_ts(date: int, is_milli: bool = False):
        datetime_obj = datetime.strptime(str(date), '%Y%m%d%H%M')

        if is_milli:
            return 1000 * int(datetime_obj.timestamp())
        
        else:
            return int(datetime_obj.timestamp())
    
    @staticmethod
    def __convert_datetime_to_iso8061(date: int):
        str_date = str(date)
        return f'{str_date[:4]}-{str_date[4:6]}-{str_date[6:8]}T{str_date[8:10]}:{str_date[10:12]}:00Z'
    
    @staticmethod
    def __determine_interval(interval: str):
        if 'm' in interval:
            return f'minutes/{interval[:-1]}'

        elif 'd' in interval:
            return 'days'
        
        elif 'w' in interval:
            return 'weeks'
        
        elif 'M' in interval:
            return 'months'
        
        else:
            raise ValueError(f'Unsupported interval {interval}')
    
    @staticmethod
    def __parse_time_values(input_string: str):
        min_match = re.search(r'min=(\d+)', input_string)
        sec_match = re.search(r'sec=(\d+)', input_string)

        if min_match and sec_match:
            min_value = int(min_match.group(1))
            sec_value = int(sec_match.group(1))

            return min_value, sec_value
        
        else:
            return None, None
    
    async def __fetch_data_crypto(self, session, url, params, is_binance=True):
        async with session.get(url, params=params) as response:
            if is_binance:
                self.__binance_rate_count = float(response.headers.get('X-MBX-USED-WEIGHT-1M'))

            else:
                self.__upbit_rate_count_min, self.__upbit_rate_count_sec = self.__parse_time_values(response.headers.get('Remaining-Req'))
                
            return await response.json()
    
    async def __fetch_data_tradfi(self, session, url, params):
        async with session.get(url, params=params, headers=self.__headers) as response:
            return await response.json()
    
    async def __get_korea_stock_data(self, session, ticker, interval, start, end):
        url = f'{self.__naver_finance_uri}{ticker}/{interval}'

        resp = await self.__fetch_data_tradfi(session, url, params={'startDateTime': start, 'endDateTime': end})

        if 'code' not in resp:
            if 'minute' in interval:
                df = pd.DataFrame(resp)
                df.drop_duplicates(inplace=True, subset=['localDateTime'])
                df.set_index('localDateTime', inplace=True)
                df.index = pd.to_datetime(df.index, format='%Y%m%d%H%M%S')
                df.sort_index(inplace=True)
                df.ffill(inplace=True)
                
                return ticker, df
            
            else:
                df = pd.DataFrame(resp)
                df.drop_duplicates(inplace=True, subset=['localDate'])
                df.set_index('localDate', inplace=True)
                df.index = pd.to_datetime(df.index, format='%Y%m%d')
                df.sort_index(inplace=True)
                df.ffill(inplace=True)
                
                return ticker, df
        
        else:
            logging.error(f'Error on fetching: Code {resp["code"]} Msg {resp["message"]}')
            return
    
    async def __get_global_finance_data(self, session, ticker, interval, start, end):
        url = f'{self.__yahoo_finance_uri}{ticker}'
        datas = []
        interval_convert = self.__convert_interval_to_sec(interval)
        end_time = self.__convert_datetime_to_ts(end)
        last_end_time = self.__convert_datetime_to_ts(start)
        
        while end_time > last_end_time:
            start_time = end_time - interval_convert
            resp  = await self.__fetch_data_tradfi(session, url, params={'interval': interval, 'period1': start_time, 'period2': end_time})

            if resp['chart']['result'] is not None:
                try:
                    ohlcv = resp['chart']['result'][0]['indicators']['quote'][0]
                    adj_close = resp['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']
                    
                    data = {
                                'timestamp': resp['chart']['result'][0]['timestamp'],
                                'open': ohlcv['open'],
                                'high': ohlcv['high'],
                                'low': ohlcv['low'],
                                'close': ohlcv['close'],
                                'volume': ohlcv['volume'],
                                'adj_close': adj_close
                            }
                    
                    datas.append(data)

                except KeyError:
                    ohlcv = resp['chart']['result'][0]['indicators']['quote'][0]
                    
                    data = {
                                'timestamp': resp['chart']['result'][0]['timestamp'],
                                'open': ohlcv['open'],
                                'high': ohlcv['high'],
                                'low': ohlcv['low'],
                                'close': ohlcv['close'],
                                'volume': ohlcv['volume']
                            }
                    
                    datas.append(data)

                end_time = start_time
            
            else:
                logging.error('Fetcherror: {}'.format(resp['chart']['error']))
                break
        
        df = pd.concat([pd.DataFrame(data) for data in datas], axis=0)
        df.drop_duplicates(inplace=True, subset=['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.index = pd.to_datetime(df.index, unit='s')
        df.sort_index(inplace=True)
        df.ffill(inplace=True)
        
        return ticker, df

    async def __get_binance_futures_data(self, session, ticker, interval, start, end):
        candle_datas = []
        interval_convert = self.__convert_interval_to_ms(interval)
        start_time = self.__convert_datetime_to_ts(start, True)
        end_time = self.__convert_datetime_to_ts(end, True)
        temp_start = end_time - 499 * interval_convert

        if temp_start <= start_time:
            params = {'symbol': ticker, 'interval': interval, 'startTime': start_time, 'endTime': end_time}
            resp = await self.__fetch_data_crypto(session, self.__binance_futures_uri, params)
            candle_datas.append(resp)

        else:
            while temp_start > start_time:
                if self.__binance_rate_count >= 1500:
                    await asyncio.sleep(60)
                    self.__binance_rate_count = 0

                params = {'symbol': ticker, 'interval': interval, 'startTime': temp_start, 'endTime': end_time}
                resp = await self.__fetch_data_crypto(session, self.__binance_futures_uri, params)

                if 'code' not in resp:
                    candle_datas.append(resp)

                else:
                    logging.error(f'{resp}')
                    break

                end_time = temp_start
                temp_start = end_time - 499 * interval_convert
    
        df = pd.DataFrame([candle_datum for candle_data in candle_datas for candle_datum in candle_data])[[0,1,2,3,4,5,9]]
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'takerBuyBase']
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['takerBuyBase'] = df['takerBuyBase'].astype(float)
        df.drop_duplicates(inplace=True, subset=['time'])
        df.set_index('time', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        df.sort_index(inplace=True)

        return ticker, df
    
    async def __get_binance_spot_data(self, session, ticker, interval ,start, end):
        candle_datas = []
        interval_convert = self.__convert_interval_to_ms(interval)
        start_time = self.__convert_datetime_to_ts(start, True)
        end_time = self.__convert_datetime_to_ts(end, True)
        temp_start = end_time - 500 * interval_convert

        if temp_start <= start_time:
            params = {'symbol': ticker, 'interval': interval, 'startTime': start_time, 'endTime': end_time}
            resp = await self.__fetch_data_crypto(session, self.__binance_spot_uri, params)
            candle_datas.append(resp)

        else:
            while temp_start > start_time:
                if self.__binance_rate_count >= 1500:
                    await asyncio.sleep(60)
                    self.__binance_rate_count = 0

                params = {'symbol': ticker, 'interval': interval, 'startTime': temp_start, 'endTime': end_time}
                resp = await self.__fetch_data_crypto(session, self.__binance_spot_uri, params)

                if 'code' not in resp:   
                    candle_datas.append(resp)

                else:
                    logging.error(f'{resp}')
                    break
                
                end_time = temp_start
                temp_start = end_time - 500 * interval_convert
        try:
            df = pd.DataFrame([candle_datum for candle_data in candle_datas for candle_datum in candle_data])[[0,1,2,3,4,5,9]]
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'takerBuyBase']
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['takerBuyBase'] = df['takerBuyBase'].astype(float)
            df.drop_duplicates(inplace=True, subset=['time'])
            df.set_index('time', inplace=True)
            df.index = pd.to_datetime(df.index, unit='ms')
            df.sort_index(inplace=True)
            
            return ticker, df

        except KeyError:
            logging.error(f'{ticker}: Unable to make dataframe')

            return ticker, None

    async def __get_upbit_spot_data(self, session, ticker, interval, start, end):
        candle_datas = []
        end_time_param = self.__convert_datetime_to_iso8061(end)
        start_time = self.__convert_datetime_to_ts(start, True)
        end_time = self.__convert_datetime_to_ts(end, True)
        url = f'{self.__upbit_spot_uri}{self.__determine_interval(interval)}'

        while end_time > start_time:
            if self.__upbit_rate_count_min < 10:
                await asyncio.sleep(60)
                self.__upbit_rate_count_min = 600
            
            elif self.__upbit_rate_count_sec < 2:
                await asyncio.sleep(1)
                self.__upbit_rate_count_sec = 9

            else:
                params = {'market': ticker, 'count': 200, 'to': end_time_param}
                resp = await self.__fetch_data_crypto(session, url, params, False)

                candle_datas.append(resp)
                end_time_param = resp[-1]['candle_date_time_utc']
                end_time = resp[-1]['timestamp']
        
        try:
            df = pd.concat([pd.DataFrame(data) for data in candle_datas], axis=0)
            df.columns = ['market', 'time', 'time_KST', 'open', 'high', 'low', 'close', 'ts', 'amt', 'volume', 'unit']
            df.drop(columns=['market', 'time_KST', 'unit', 'ts'], inplace=True)
            df.drop_duplicates(inplace=True, subset=['time'])
            df.set_index('time', inplace=True)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
        
            return ticker, df
        
        except KeyError:
            logging.error(f'{ticker}: Unable to make dataframe')

            return ticker, None

    async def __get_multiple_korea_stock_data(self, tickers, interval, start, end):
        if interval not in FinanceDownloader.KOREA_STOCK_VALID_INTERVAL:
            raise ValueError(f'Invalid interval, Valid interval is {FinanceDownloader.KOREA_STOCK_VALID_INTERVAL}')

        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_korea_stock_data(session, ticker, interval, start, end) for ticker in tickers]

            return dict(await asyncio.gather(*tasks))
    
    async def __get_multiple_global_finance_data(self, tickers,  interval, start, end):
        if interval not in FinanceDownloader.GLOBAL_FINANCE_DATA_VALID_INTERVAL:
            raise ValueError(f'Invalid interval, Valid interval is {FinanceDownloader.GLOBAL_FINANCE_DATA_VALID_INTERVAL}')
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_global_finance_data(session, ticker, interval, start, end) for ticker in tickers]

            return dict(await asyncio.gather(*tasks))

    async def __get_multiple_binance_spot_data(self, tickers, interval, start, end):
        if interval not in FinanceDownloader.CRYPTO_BINANCE_VALID_INTERVAL:
            raise ValueError(f'Invalid interval, Valid interval is {FinanceDownloader.CRYPTO_BINANCE_VALID_INTERVAL}')

        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_binance_spot_data(session, ticker, interval, start, end) for ticker in tickers]

            return dict(await asyncio.gather(*tasks))

    async def __get_multiple_binance_futures_data(self, tickers, interval, start, end):

        if interval not in FinanceDownloader.CRYPTO_BINANCE_VALID_INTERVAL:
            raise ValueError(f'Invalid interval, Valid interval is {FinanceDownloader.CRYPTO_BINANCE_VALID_INTERVAL}')
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_binance_futures_data(session, ticker, interval, start, end) for ticker in tickers]

            return dict(await asyncio.gather(*tasks))
    
    async def __get_multiple_upbit_spot_data(self, tickers, interval, start, end):
        if interval not in FinanceDownloader.CRYTPO_UPBIT_VALID_INTERVAL:
            raise ValueError(f'Invalid interval, Valid interval is {FinanceDownloader.CRYTPO_UPBIT_VALID_INTERVAL}')
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_upbit_spot_data(session, ticker, interval, start, end) for ticker in tickers]

            return dict(await asyncio.gather(*tasks))
    
    def download_data(self, download_type, tickers, interval, start, end):
        '''
        Datetime Format: YYYYMMDDHHMM
        '''
        if download_type not in FinanceDownloader.AVAILABLE_DOWNLOAD_TYPE:
            raise ValueError(f'Invalid download type, Valid type is {FinanceDownloader.AVAILABLE_DOWNLOAD_TYPE}')
        
        else:
            if download_type == 'KOREA_STOCK':
                return asyncio.run(self.__get_multiple_korea_stock_data(tickers, interval, start, end))
            
            elif download_type == 'GLOBAL_FINANCE':
                return asyncio.run(self.__get_multiple_global_finance_data(tickers, interval, start, end))
            
            elif download_type == 'CRYPTO_SPOT_BINANCE':
                return asyncio.run(self.__get_multiple_binance_spot_data(tickers, interval, start, end))
            
            elif download_type == 'CRYPTO_FUTURES_BINANCE':
                return asyncio.run(self.__get_multiple_binance_futures_data(tickers, interval, start, end))
            
            elif download_type == 'CRYPTO_SPOT_UPBIT':
                return asyncio.run(self.__get_multiple_upbit_spot_data(tickers, interval, start, end))
