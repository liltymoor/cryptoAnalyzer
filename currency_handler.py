import asyncio


from datetime import datetime, timedelta
from table_imports import pd
from binance_imports import Client
from dataframe_handler import DataFrameCollector
from constants import INDICATORS_VOCABULARY
from indicators.ta_indicators_fill import *

# TODO make it run cycles asynchronously


class LiveCycler:
    def __init__(self, currency_set):
        self.currency_set = currency_set

        self.__interval_loop = 0.01

    def set_check_interval(self, interval: float):
        self.__interval_loop = interval

    def live_loop(self):
        for currency in self.currency_set:
            if datetime.now() >= currency.get_exec_time():
                currency.get_live()
                currency.calculate_indicators()
                currency.print_info()



class CurrencyLiveCycle:
    def __init__(self, client: Client, pair: str, interval: str):
        self.__binance_client = client

        self.currency_pair = pair
        self.interval = interval

        self.__df_collector = DataFrameCollector(client, pair, interval)
        self.__df = self.__df_collector.live_collect()
        self.__ind_df = pd.DataFrame()
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

    def get_live(self):
        if self.__df is None:
            self.__df = self.__df_collector.live_collect()
        else:
            self.__df = self.__df_collector.live_collect(self.__df)

        self.valid_time()

    def print_info(self):
        print("Currency:", self.currency_pair, "Interval:", self.interval, "Next load time:", self.__execute_time)
        print(self.__df.to_string())
        print(self.__ind_df.to_string())

    def calculate_indicators(self):
        calc = IndicatorsCalculator(self.__df, self.__ind_df)
        self.__ind_df = asyncio.run(calc.calculate())


class IndicatorsCalculator:
    def __init__(self, df: pd.DataFrame, ind_df: pd.DataFrame):
        self.__df = df
        self.__ind_df = ind_df

        # TODO перенести лист в константы
        self.__inds = ["RSI"]

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

        return self.__ind_df

    async def __ind_resolver(self, calc_q, completed):
        while not calc_q.empty():
            indicator = await calc_q.get()
            # fetching the indicator to calculate from queue
            # 0 always means that there will be a function to fill the indicators value
            # at some points it can be None.
            self.__ind_df = INDICATORS_VOCABULARY[indicator][0](self.__df, self.__ind_df)
            completed[0] += 1

