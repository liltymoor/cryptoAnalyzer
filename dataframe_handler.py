import time

import aiohttp
import pandas as pd

from constants import DF_COLUMNS_TIMED
from exceptions import LoadDataframeBinanceException
from binance_imports import Client
from table_imports import *

from currency_region_loader import RegionController

from datetime import *
import time
import requests
import json, sys

class DataFrameCollector:
    def __init__(self, binance_client: Client, pair: str, session: aiohttp.ClientSession = None, interval="1m"):
        self.binance_client = binance_client
        self.binance_pair = pair
        self.collect_interval = interval
        self.session = session
    @staticmethod
    def debug_msg(*msg):
         print("[DF_COLLECTOR]", ' '.join([str(i) for i in msg]))

    async def __binance_df(self, stock, interval, startDate: datetime = None, endDate: datetime = None):
        # Getting UTC format time
        now = datetime.utcnow()
        # TODO через некоторое время подчистить не нужные комменты

        # Getting last updates from binance client
        # This method is 0.3 sec
        response_content = None
        if startDate: # if we're getting the period of data, then we're using another get request
            startDate = int(datetime.timestamp(startDate) * 1000)
            endDate = int(datetime.timestamp(endDate) * 1000)
            async with self.session.get("https://data.binance.com/api/v3/klines",
                                        params={
                                          'symbol': stock,
                                          'interval': interval,
                                          'startTime': startDate,
                                          'endTime': endDate,
                                          'limit': 730}) as resp:
                response_content = await resp.json()
        else: # otherwise we're using this request to get the latest frames
            async with self.session.get(f"https://data.binance.com/api/v3/klines?symbol={stock}&interval={interval}") as resp:
                response_content = await resp.json()

        #response_content = await historical.json() # may be awaited
        #print(response_content)
        #print(len(response_content))

        # This method is too slow (0.5 sec)
        # response_content = self.binance_client.get_historical_klines(
        #     stock, interval, str(start_date))

        # Setting the pandas dataframe and its columns

        df = None
        if startDate: # if we're getting a period of data, then we're indexing all the frames we got.
            df = pd.DataFrame([content[1:] for content in response_content],
                              index=[pd.to_datetime(content[0] / 1000, unit='s') + timedelta(hours=3)
                                     for content in response_content])
        else:
              # otherwise we're indexing the -2 frame, that is not last
              # because last frame is current frame that is not finished yet
            df = pd.DataFrame([response_content[-2][1:]],
                              index=[pd.to_datetime(response_content[-2][0] / 1000, unit='s') + timedelta(hours=3)])
        df.columns = DF_COLUMNS

        # Formatting given time from binance
        #df['Open Time'] = pd.to_datetime(df['Open Time'] / 1000, unit='s') + timedelta(hours=3)
        df['Close Time'] = pd.to_datetime(df['Close Time'] / 1000, unit='s') + timedelta(hours=3)

        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)
        return df

    async def live_collect(self,
                     interval: str,
                     live_df=None,
                     startDate: datetime = None,
                     endDate: datetime = None ):
        """ (Async version) Collect Pandas df easily with binance client, pair, interval and optionally startDate and endDate.
        If live_df is None (default case) - it will return the last collected df."""

        df = None
        if startDate:
            df = await self.__binance_df(str(self.binance_pair), interval, startDate=startDate, endDate=endDate)
        else:
            df = await self.__binance_df(str(self.binance_pair), interval)

        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            print()
            DataFrameCollector.debug_msg(self.binance_pair, interval, "data collected at", datetime.now())
            return pd.concat([live_df, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException

    def __binance_notlive_df(
            self, stock, interval, index_func,
            startDate: datetime = None, endDate: datetime = None,):
        # Getting UTC format time
        now = datetime.utcnow()

        # Getting last updates from binance client
        # This method is 0.3 sec
        historical = None
        if startDate: # if we're getting the period of data, then we're using another get request
            startDate = int(datetime.timestamp(startDate) * 1000)
            endDate = int(datetime.timestamp(endDate) * 1000)
            historical = requests.get("https://data.binance.com/api/v3/klines",
                                      params={
                                          'symbol': stock,
                                          'interval': interval,
                                          'startTime': startDate,
                                          'endTime': endDate,
                                          'limit': 720})
        else: # otherwise we're using this request to get the latest frames
            historical = requests.get(f"https://data.binance.com/api/v3/klines?symbol={stock}&interval={interval}")

        response_content = historical.json() # may be awaited
        #print(response_content)
        #print(len(response_content))

        # This method is too slow (0.5 sec)
        # response_content = self.binance_client.get_historical_klines(
        #     stock, interval, str(start_date))

        # Setting the pandas dataframe and its columns

        df = None
        if startDate: # if we're getting a period of data, then we're indexing all the frames we got.
            if index_func is datetime:
                df = pd.DataFrame([content[1:] for content in response_content],
                                  index=[pd.to_datetime(content[0] / 1000, unit='s') + timedelta(hours=3)
                                         for content in response_content],
                                  columns=DF_COLUMNS)
            elif index_func is int:
                df = pd.DataFrame([content for content in response_content],
                                  index=[list(range(len(response_content)))],
                                  columns=DF_COLUMNS_TIMED)
        else:
              # otherwise we're indexing the -2 frame, that is not last
              # because last frame is current frame that is not finished yet
            df = pd.DataFrame([response_content[-2][1:]],
                              index=[pd.to_datetime(response_content[-2][0] / 1000, unit='s') + timedelta(hours=3)])
            df.columns = DF_COLUMNS
        # Formatting given time from binance
        df['Close Time'] = pd.to_datetime(df['Close Time'] / 1000, unit='s') + timedelta(hours=3)

        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)
        return df

    def collect(self,
                interval: str,
                live_df=None,
                startDate: datetime = None,
                endDate: datetime = None,
                index_func = datetime):
        """ (Sync version) Collect Pandas df easily with binance client, pair, interval and optionally startDate and endDate.
                If live_df is None (default case) - it will return the last collected df."""

        df = None
        if startDate:
            df = self.__binance_notlive_df(str(self.binance_pair), interval, index_func, startDate=startDate, endDate=endDate)
        else:
            df = self.__binance_notlive_df(str(self.binance_pair), interval, index_func)

        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            return pd.concat([live_df, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException

    def binance_big_df_collect(self, interval, start_date, end_date, index_func=datetime):
        start_date = str(start_date)
        end_date = str(end_date)

        response_content = self.binance_client.get_historical_klines(
            self.binance_pair, interval, start_date, end_date, limit=100)

        df = None
        if index_func is datetime: # datetime indexes is the actual time of the frame
            df = pd.DataFrame([content[1:] for content in response_content],
                              index=[pd.to_datetime(content[0] / 1000, unit='s') + timedelta(hours=3)
                                     for content in response_content],
                              columns=DF_COLUMNS)
        elif index_func is int: # int indexes is 1,2,3,4,5,6
            df = pd.DataFrame([content for content in response_content],
                              index=[list(range(len(response_content)))],
                              columns=DF_COLUMNS_TIMED)

            df['Open Time'] = pd.to_datetime(df['Open Time'] / 1000, unit='s') + timedelta(hours=3)

        df['Close Time'] = pd.to_datetime(df['Close Time'] / 1000, unit='s') + timedelta(hours=3)

        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)

        return df
    def collect_big_data(self,
                         interval: str = '1m',
                         start_date: datetime = None,
                         end_date: datetime = None):

        period_delta = end_date - start_date

        # if period is more than 1 day we re using special class
        if (int(period_delta.seconds / 60)) > 720:
            region = RegionController(self, interval, start_date, end_date)
            region_df = None
            remain_iters = region.get_remaining()
            for i in range(remain_iters):
                next_region_df = region.next()
                region_df = pd.concat([region_df, next_region_df], ignore_index=False)

            return region_df

        df = self.binance_big_df_collect(interval, start_date, end_date)

        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            return pd.concat([None, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException