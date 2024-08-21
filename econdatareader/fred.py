import aiohttp
import asyncio
import pandas as pd
import nest_asyncio
import logging

from datetime import datetime


class FredDownloader(object):
    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__uri = 'https://api.stlouisfed.org/fred'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.__nan_char = '.'
        
        nest_asyncio.apply()

    @staticmethod
    def __compare_date(date_1: str, date_2: str, compare_type: str):
        if compare_type == 'min':
            return datetime.strftime(min(datetime.strptime(date_1, '%Y-%m-%d'), datetime.strptime(date_2, '%Y-%m-%d')), '%Y-%m-%d')
        
        elif compare_type == 'max':
            return datetime.strftime(max(datetime.strptime(date_1, '%Y-%m-%d'), datetime.strptime(date_2, '%Y-%m-%d')), '%Y-%m-%d')
        
        else:
            raise ValueError('Invalid compare type')
    
    def __convert_to_float(self, value: str):
        if value == self.__nan_char:
            return float('nan')

        else:
            return float(value.replace(',', ''))
    
    async def __fetch_data(self, session, url, params):
        async with session.get(url, params=params, headers=self.__headers) as response:
            return await response.json()
    

    async def __get_series_info(self, session, series_id):
        url = f'{self.__uri}/series'
        resp = await self.__fetch_data(session, url, params={'api_key': self.__api_key, 'series_id': series_id, 'file_type': 'json'})

        return resp
    
    async def __get_series(self, session, series_id, start, end):
        series_info = await self.__get_series_info(session, series_id)

        try:
            adjusted_start = self.__compare_date(series_info['seriess'][0]['observation_start'], start, 'max')
            adjusted_end = self.__compare_date(series_info['seriess'][0]['observation_end'], end, 'min')
            url = f'{self.__uri}/series/observations'

            resp = await self.__fetch_data(session, url, params={'api_key': self.__api_key, 'series_id': series_id, 'observation_start': adjusted_start, 'observation_end': adjusted_end, 'file_type': 'json'})
            resp_dict = [{'date': observation['date'], 'value': self.__convert_to_float(observation['value'])} for observation in resp['observations']]

            df = pd.DataFrame(resp_dict)
            df.set_index('date', inplace=True)
            df['value'] = df['value'].astype(float)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)

            return series_id, df
        
        except KeyError:
            logging.error(f'Invalid series id: {series_id}')

            return series_id, None

    async def __get_multiple_series(self, series_ids, start, end):
        async with aiohttp.ClientSession() as session:
            tasks = [self.__get_series(session, series_id, start, end) for series_id in series_ids]

            return dict(await asyncio.gather(*tasks))

    def download_data(self, series_ids, start, end):
        return asyncio.run(self.__get_multiple_series(series_ids, start, end))
