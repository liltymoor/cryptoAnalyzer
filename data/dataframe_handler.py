import subprocess
import time

import aiohttp
import pandas as pd

from constants import DF_COLUMNS_TIMED
from exceptions import LoadDataframeBinanceException
from binance_imports import Client
from table_imports import *

from data.currency_region_loader import RegionController

from datetime import *
import time
import requests
import json, sys

import multiprocessing as mp
import concurrent.futures


class DataFrameCollector:

    datetime_mapping = 's'
    datetime_divider = 1000
    gmt_delta = timedelta(hours=3)

    def __init__(self, binance_client: Client, pair: str, session: aiohttp.ClientSession=None, interval="1m"):
        self.binance_client = binance_client
        self.binance_pair = pair
        self.collect_interval = interval
        self.session = session
    @staticmethod
    def debug_msg(*msg):
         print("[DF_COLLECTOR]", ' '.join([str(i) for i in msg]))

    @staticmethod
    def index_columns(df: pd.DataFrame, index_func=datetime):
        result = None
        if index_func is datetime:
            index_column = \
                [datetime.fromtimestamp(time / DataFrameCollector.datetime_divider) for time in df["Open Time"]]
            df.drop("Open Time", axis=1)

            result = pd.DataFrame(df, index=index_column, columns=DF_COLUMNS)
        elif index_func is int:
            df["Open Time"] = [datetime.fromtimestamp(time / DataFrameCollector.datetime_divider) for time in df["Open Time"]]
            result = pd.DataFrame(df, columns=DF_COLUMNS_TIMED)

        result["Close Time"] = [datetime.fromtimestamp(time / DataFrameCollector.datetime_divider) for time in df["Close Time"]]

        return result


    async def __binance_df(self, stock, interval, startDate: datetime = None, endDate: datetime = None, index_func=datetime):
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
            df = pd.DataFrame([content for content in response_content],
                              columns=DF_COLUMNS_TIMED)
        else:
              # otherwise we're indexing the -2 frame, that is not last
              # because last frame is current frame that is not finished yet
            df = pd.DataFrame([response_content[-2]],
                                columns=DF_COLUMNS_TIMED)



        # Formatting given time from binance
        #df['Close Time'] = pd.to_datetime(df['Close Time'] / self.datetime_divider, unit=self.datetime_mapping) + timedelta(hours=3)
        df = DataFrameCollector.index_columns(df, index_func)
        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)
        return df

    async def live_collect(self,
                     interval: str,
                     live_df=None,
                     startDate: datetime = None,
                     endDate: datetime = None, index_func=datetime):
        """ (Async version) Collect Pandas df easily with binance client, pair, interval and optionally startDate and endDate.
        If live_df is None (default case) - it will return the last collected df."""

        df = None
        if startDate:
            df = await self.__binance_df(str(self.binance_pair), interval, startDate=startDate, endDate=endDate, index_func=index_func)
        else:
            df = await self.__binance_df(str(self.binance_pair), interval, index_func=index_func)

        live_len = len(live_df)
        indexes = []
        for row in range(len(df)):
            indexes.append(live_len)
            live_len += 1

        index = pd.Index(indexes)
        df = df.set_index(index)

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
        response_content = None
        if startDate:  # if we're getting the period of data, then we're using another get request\
            startDate = int(datetime.timestamp(startDate) * 1000)
            endDate = int(datetime.timestamp(endDate) * 1000)
            historical = requests.get("https://data.binance.com/api/v3/klines",
                                      params={
                                          'symbol': stock,
                                          'interval': interval,
                                          'startTime': startDate,
                                          'endTime': endDate,
                                          'limit': 1000})

        else:  # otherwise we're using this request to get the latest frames
            historical = requests.get(f"https://data.binance.com/api/v3/klines?symbol={stock}&interval={interval}")

        response_content = historical.json()  # may be awaited
        # Setting the pandas dataframe and its columns



        df = None
        try:
            if startDate:  # if we're getting a period of data, then we're indexing all the frames we got.
                df = pd.DataFrame([content for content in response_content],
                                    columns=DF_COLUMNS_TIMED)
            else:
                # otherwise we're indexing the -2 frame, that is not last
                # because last frame is current frame that is not finished yet
                df = pd.DataFrame([response_content[-2]],
                                  columns=DF_COLUMNS_TIMED)
        except TypeError:
            print(response_content)

        df = DataFrameCollector.index_columns(df, index_func)

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

        df = pd.DataFrame([content for content in response_content],
                            columns=DF_COLUMNS_TIMED)

        df = DataFrameCollector.index_columns(df, index_func)
        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)

        return df

    def next_region(self, region, start_date, end_date, index_func=datetime):
        return region.get_df_piece(start_date, end_date, index_func=index_func)

    def collect_big_data(self,
                         interval: str = '1m',
                         start_date: datetime = None,
                         end_date: datetime = None,
                         index_func=datetime):

        period_delta = end_date - start_date

        # if period is more than 1 day we re using special class
        if (int(period_delta.total_seconds() / 60)) > self.datetime_divider:
            start_datetime = datetime.now()

            region = RegionController(self, interval, start_date, end_date)
            region_df = None
            remain_iters = region.get_remaining()

            dfs = {}

            # self.next_region(region, start_date, end_date)

            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:

                future_to_index = {}
                region_start_date = start_date

                for i in range(remain_iters):
                    future_to_index[
                        executor.submit(self.next_region, region,
                                        region_start_date, region_start_date + timedelta(hours=16, minutes=40), index_func=index_func)
                    ] = i

                    region_start_date += timedelta(hours=16, minutes=40)

                for future in concurrent.futures.as_completed(future_to_index):
                    i = future_to_index[future]
                    dfs[i] = future.result()

            dfs = dict(sorted(dfs.items()))
            region_df = pd.concat(dfs.values())


            end_datetime = datetime.now()
            time_difference = end_datetime - start_datetime

            print(f'Time: {time_difference.total_seconds()} seconds')

            return region_df

        df = self.binance_big_df_collect(interval, start_date, end_date)

        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            return pd.concat([None, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException