import time

import aiohttp
import pandas as pd

from exceptions import LoadDataframeBinanceException
from binance_imports import Client
from table_imports import *

from datetime import *
import time
import requests
import json, sys

class DataFrameCollector:
    def __init__(self, binance_client: Client, pair: str, session: aiohttp.ClientSession, interval="1m"):
        self.binance_client = binance_client
        self.binance_pair = pair
        self.collect_interval = interval
        self.session = session

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

    # TODO not-live collect for some period of time
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
            print(self.binance_pair, interval, "data collected at", datetime.now())
            return pd.concat([live_df, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException

    def __binance_notlive_df(self, stock, interval, startDate: datetime = None, endDate: datetime = None):
        # Getting UTC format time
        now = datetime.utcnow()
        # TODO через некоторое время подчистить не нужные комменты

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
                                          'limit': 730})
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

    def collect(self,
                interval: str,
                live_df=None,
                startDate: datetime = None,
                endDate: datetime = None ):
        """ (Sync version) Collect Pandas df easily with binance client, pair, interval and optionally startDate and endDate.
                If live_df is None (default case) - it will return the last collected df."""

        df = None
        if startDate:
            df = self.__binance_notlive_df(str(self.binance_pair), interval, startDate=startDate, endDate=endDate)
        else:
            df = self.__binance_notlive_df(str(self.binance_pair), interval)

        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            return pd.concat([live_df, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException