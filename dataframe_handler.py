import time

import aiohttp

from exceptions import LoadDataframeBinanceException
from binance_imports import Client
from table_imports import *

from datetime import *
import time
import requests
import json, sys

class DataFrameCollector:
    def __init__(self, binance_client: Client, pair: str, interval="1m"):
        self.binance_client = binance_client
        self.binance_pair = pair
        self.collect_interval = interval

    def __binance_df(self, stock, interval):
        # Getting UTC format time
        now = datetime.utcnow()
        # TODO через некоторое время подчистить не нужные комменты
        #start_date = now - timedelta(minutes=1, seconds=now.second, microseconds=now.microsecond)

        # Getting last updates from binance client
        # This method is 0.3 sec
        historical = requests.get(
            f"https://data.binance.com/api/v3/klines?symbol={stock}&interval={interval}")
        # historical = await aiohttp.request(
        #     'GET', f"https://data.binance.com/api/v3/klines?symbol={stock}&interval={interval}")


            # could be used to get different selections
            #"&startTime=" + starttime + "&endTime=" + endtime
        response_content = historical.json() # may be awaited

        # This method is too slow (0.5 sec)
        # response_content = self.binance_client.get_historical_klines(
        #     stock, interval, str(start_date))

        # Setting the pandas dataframe and its columns
        df = pd.DataFrame([response_content[-2]])
        df.columns = DF_COLUMNS

        # Formatting given time from binance
        df['Open Time'] = pd.to_datetime(df['Open Time'] / 1000, unit='s') + timedelta(hours=3)
        df['Close Time'] = pd.to_datetime(df['Close Time'] / 1000, unit='s') + timedelta(hours=3)

        # Mapping specific columns to numeric value
        df[DF_NUMERIC_COLUMNS] = df[DF_NUMERIC_COLUMNS].apply(pd.to_numeric, axis=1)
        return df

    # TODO not-live collect for some period of time
    def live_collect(self, live_df=None):
        """Collect Pandas df easily with binance client, pair and given interval.
        If live_df is None (default case) - it will return the last collected df."""
        start_time = time.time()
        print("Fetching started at", start_time)
        # TODO добавить поддержку остальных интервалов

        df = self.__binance_df(str(self.binance_pair), '1m')

        print("Fetching started at", time.time() - start_time)
        if df is not None:
            # if given df is None, or its None by default - this will return the collected df
            return pd.concat([live_df, df], ignore_index=False)
        else:
            raise LoadDataframeBinanceException
