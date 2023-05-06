import asyncio


from datetime import datetime, timedelta

import aiohttp

from table_imports import pd
from binance_imports import Client
from dataframe_handler import DataFrameCollector
from constants import INDICATORS_VOCABULARY
from indicators.ta_indicators_fill import *
from PyQt6 import QtCore

# TODO make it run cycles asynchronously

class LiveCycler:
    def __init__(self, client, currency_set, signal: QtCore.pyqtSignal):
        self.client = client
        self.currencies = []
        self.interval_loop = 0.01
        self.signal = signal
        self.session: aiohttp.ClientSession = None

        for pair, interval in currency_set:
            self.currencies.append(CurrencyLiveCycle(self.client, pair, interval, self.session))



    def set_check_interval(self, interval: float):
        self.interval_loop = interval

    def add_currency(self, pair, interval):
        # this one returns currency to notify whenever it will be updated
        self.currencies.append(CurrencyLiveCycle(self.client, pair, interval, self.session))
        return self.currencies[-1]
    async def setup_async_session(self):
        self.session = aiohttp.ClientSession()

    async def live_loop(self):
        for currency in self.currencies:
            #currency.check_lost_frames()
            if datetime.now() >= currency.get_exec_time():
                await currency.get_live()
                #currency.calculate_indicators() #TODO refactor
                currency.print_info()
                self.signal.emit(currency.get_dataframes())



class CurrencyLiveCycle(QtCore.QObject):
    updated = QtCore.pyqtSignal(pd.DataFrame)
    def __init__(self, client: Client, pair: str, interval: str, session: aiohttp.ClientSession):
        super(CurrencyLiveCycle,self).__init__()
        self.__binance_client = client

        self.currency_pair = pair
        self.interval = interval

        self.__df_collector = DataFrameCollector(client, pair, session, interval)

        #getting 1440 frames (1 day)
        self.__df = self.__df_collector.collect(
            self.interval,
            startDate=self.__get_next_time() - timedelta(hours=12, minutes=2),
            endDate=self.__get_next_time() - timedelta(minutes=2)
        )
        self.__last_updated = datetime.now()

        # TODO columns to constants
        self.__ind_df = pd.DataFrame({'RSI': [], 'PPO': [], 'PPO_SIGNAL': []})
        self.__execute_time = self.__get_next_time()
        self.print_info()

    def __get_next_time(self):
        if self.interval[-1] == "m":
            # calculating how many seconds remains to complete new check
            sec_next_exec = timedelta(minutes=float(self.interval[0:-1])).seconds - datetime.now().second
            next_exec = datetime.now() + timedelta(seconds=sec_next_exec + 1)
            return next_exec
        elif self.interval[-1] == "h":
            min_next_exec = (timedelta(hours=float("1")).seconds / 60) - datetime.now().minute
            next_exec = datetime.now() + timedelta(minutes=min_next_exec) - timedelta(seconds=datetime.now().second)
            return next_exec

    def valid_time(self):
        if datetime.now() >= self.__execute_time:
            self.__execute_time = self.__get_next_time()

    def get_exec_time(self):
        return self.__execute_time

    async def get_live(self):
        self.__df = await self.__df_collector.live_collect(self.interval, live_df=self.__df)
        self.__last_updated = datetime.now()
        self.valid_time()
        self.updated.emit(self.__df)

    def get_period(self, period_start: datetime, period_end: datetime):
        self.__df = self.__df_collector.live_collect(self.__df, period_start, period_end)
        self.__last_updated = datetime.now()

    def check_lost_frames(self):
        delta = None
        if self.interval == '1m':
            delta = timedelta(minutes=1)
        elif self.interval == '1h':
            delta = timedelta(hours=1)
        else: return # TODO add an exception here

        if (datetime.now() - self.__last_updated) > delta:
            print("Lost frames were found. Fetching them")
            self.get_period(self.__last_updated, self.__get_next_time() - delta)
            self.updated.emit(self.__df)


    def print_info(self):
        print("Currency:", self.currency_pair, "Interval:", self.interval, "Next load time:", self.__execute_time)
        #print(self.__df.to_string())
        #print(self.__ind_df.to_string())

    def calculate_indicators(self):
        calc = IndicatorsCalculator(self.__df, self.__ind_df)
        self.__ind_df = asyncio.run(calc.calculate())

    def get_dataframes(self):
        return (self.__df, self.__ind_df)

    def window_created(self):
        # called once, when the window init complete
        self.updated.emit(self.__df)


class IndicatorsCalculator:
    def __init__(self, df: pd.DataFrame, ind_df: pd.DataFrame):
        self.__df = df
        self.__ind_df = ind_df
        self.__new_row = pd.DataFrame()
        self.__inds = ["RSI", "PPO"]

    async def calculate(self):
        calc_q = asyncio.Queue()
        for ind in self.__inds:
            await calc_q.put(ind)

        # these crutches were made to make tasks increment it as well as it can be done in this namespace
        elapsed_inds = [0]

        #with Timer(text=f"[{elapsed_inds}]"+"\nTotal calculating time : {:.1f}"):
        await asyncio.gather(
            asyncio.create_task(self.__ind_resolver(calc_q, elapsed_inds))
        )
        self.__ind_df = self.__new_row
        return self.__ind_df

    async def __ind_resolver(self, calc_q, completed):
        while not calc_q.empty():
            indicator = await calc_q.get()
            # fetching the indicator to calculate from queue
            # 0 always means that there will be a function to fill the indicators value
            # at some points it can be None.
            self.__new_row = INDICATORS_VOCABULARY[indicator][0](self.__df, self.__new_row)
            completed[0] += 1

