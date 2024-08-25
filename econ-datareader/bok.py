import aiohttp
import asyncio
import requests
import re
import pandas as pd
import nest_asyncio
import logging
import re

from typing import List, Tuple


class BokDownloader(object):
    AVAILABLE_PERIOD = ['A', 'Q', 'M', 'D']
    VALID_FORMATS = {'A': r'^\d{4}$', 'Q':  r'^\d{4}Q[1-4]$', 'M': r'^\d{4}(0[1-9]|1[0-2])$', 'D':  r'^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$'}

    def __init__(self, api_key):
        self.__api_key = api_key
        self.__uri = 'https://ecos.bok.or.kr/api'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        self.available_stats = self.__get_stat_table_list()

        nest_asyncio.apply()
    
    def __check_format(self, period, input_date):
        if re.match(BokDownloader.VALID_FORMATS[period], input_date):
            return True
        
        else:
            return False
    
    @staticmethod
    def __convert_to_datetime(period, index):
        if period == 'A':
            return pd.to_datetime(index,  format='%Y') + pd.offsets.YearEnd(0)
        
        elif period == 'Q':
            pd.to_datetime(index.apply(lambda x: pd.Period(x, freq='Q').start_time)) + pd.offsets.QuarterEnd()

        elif period == 'M':
            return pd.to_datetime(index, format='%Y%m') + pd.DateOffset(day=1)
        
        elif period == 'D':
            return pd.to_datetime(index, format='%Y%m%d')

        else:
            raise ValueError('Invalid period')
    
    def __get_stat_table_list(self):
        url = f'{self.__uri}/StatisticTableList/{self.__api_key}/json/kr/1/99999/'

        try:
            response = requests.get(url=url).json()
            datas = response['StatisticTableList']['row']
            
            for data in datas:
                data['STAT_NAME'] = re.sub(r'\d+\.', '', data['STAT_NAME'])
            
            df = pd.DataFrame(datas)

            return df
        
        except KeyError:
            logging.error('Error in fetching table.')

    
    def search_stat_code_by_keyword(self, keyword: str):
        return self.available_stats.query(f"STAT_NAME.str.contains('{keyword}')")


    async def __fetch_data(self, session, url):
        async with session.get(url, headers=self.__headers) as response:
            return await response.json()
    
    async def __get_series(self, session, stat_code, period, start, end, item_code):
        if period not in BokDownloader.AVAILABLE_PERIOD:
            raise ValueError('Invalid period')
        
        elif (self.__check_format(period, start) or self.__check_format(period, end)) is False:
            raise ValueError('Invalid date format')

        url = f'{self.__uri}/StatisticSearch/{self.__api_key}/json/en/1/10000/{stat_code}/{period}/{start}/{end}/{item_code}'
        raw_datas = await self.__fetch_data(session, url)

        try:
            data = [{'time': raw_data['TIME'], 'value': float(raw_data['DATA_VALUE'].replace(',', ''))} for raw_data in raw_datas['StatisticSearch']['row']]
            df = pd.DataFrame(data)
            df['value'] = df['value'].astype(float)
            df.set_index('time', inplace=True)
            df.index = self.__convert_to_datetime(period, df.index)

            return f'{stat_code}-{item_code}', df

        except KeyError:
            logging.error(f'Invalid series id: {stat_code}-{item_code}')

            return f'{stat_code}-{item_code}', None
    
    async def __get_multiple_series(self, request_infos: List[Tuple[str]]):
        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_series(session, request_info[0], request_info[2], request_info[3], request_info[4], request_info[1]) for request_info in request_infos]

            return dict(await asyncio.gather(*tasks))
        
    def download_data(self, request_infos: List[Tuple[str]]):
        return asyncio.run(self.__get_multiple_series(request_infos))
