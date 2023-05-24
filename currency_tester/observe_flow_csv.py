import shutil
from datetime import datetime
import sys
sys.path.insert(1, '../')
from binance_imports import Client
import sqlite3
import indicators.ta_indicators_fill
from data.dataframe_handler import DataFrameCollector
from sys import argv
from inspect import getmembers, isfunction
from constants import ISCHIMOKU_DISPLACEMENT
from api_keys import *
from functions import fill_data
from indicators import ta_indicators_fill
from sys import argv
import os
import pandas as pd







def csv_flow():
    stock = argv[1]
    start_date = datetime.fromisoformat(argv[2])
    end_date = datetime.fromisoformat(argv[3])
    timeframe = argv[4]
    flow_number = int(argv[5])
    strategy = argv[6]

    client = Client(API_KEY, SECRET_KEY)

    for i in range(1):
        str_start = str(start_date)
        str_end = str(end_date)

        df_collector = DataFrameCollector(
            client, stock, interval=timeframe)

        data = df_collector.binance_big_df_collect(
            timeframe, start_date, end_date, int)

        data = fill_data(data)

        fill_functions = getmembers(ta_indicators_fill, isfunction)

        incorrect_function_names = ['fill_breakout_signals', 'fill_cross_signals', 'fill_ind_signals',
                                    'shift']

        for fill_function in fill_functions:
            if not (fill_function[-1].__name__ in incorrect_function_names):
                data = fill_function[-1](data)

        # Deleting Ichimoku diplacement
        index_need_to_delete = [i for i in range(ISCHIMOKU_DISPLACEMENT * 3)]
        index_need_to_delete.extend([len(data) - i - 1 for i in range(ISCHIMOKU_DISPLACEMENT + 1)])
        index_need_to_delete.sort()

        data.drop(labels=index_need_to_delete, axis=0, inplace=True)
        data.to_csv(f'exported_info/csv/combine_tmp/Flow-{flow_number}.csv',
                    mode='a', header=True)
        del data
        del df_collector
    client.close_connection()


def combine_to_csv(stock, iteration: int, flow_count):
    total_df = None

    for i in range(flow_count):

        if i == 0:
            total_df = pd.read_csv(f'exported_info/csv/combine_tmp/Flow-{str(i)}.csv')
            total_df.drop(total_df.columns[[0]], axis=1, inplace=True)
        else:
            df = pd.read_csv(f'exported_info/csv/combine_tmp/Flow-{str(i)}.csv')
            df.drop(df.columns[[0]], axis=1, inplace=True)
            total_df = pd.concat([total_df, df], ignore_index=True)
            del df

    print(f"Month {iteration + 1} is ready")

    dir_csv_path = f'exported_info/csv/{str(stock)}'
    db_to_copy   = f'exported_info/db/buffer/total_test_info.db'
    dir_df_path  = f'exported_info/db/{str(stock)}'

    try:
        os.mkdir(dir_csv_path)
    except Exception:
        pass

    try:
        os.mkdir(dir_df_path)
    except Exception:
        pass

    try:
        os.mkdir(dir_df_path + "/" + f"Month-{iteration + 1}\\")
    except Exception:
        pass

    shutil.copy(db_to_copy, dir_df_path + "/" + f"Month-{iteration + 1}/total_test_info.db")
    conn = sqlite3.connect(dir_df_path + "/" + f"Month-{iteration + 1}/total_test_info.db")

    cur = conn.cursor()
    cur.execute('VACUUM;')

    conn.commit()
    conn.close()

    print(f'{dir_csv_path}/Month-{str(iteration + 1)}.csv')

    total_df.to_csv(
        f'{dir_csv_path}/Month-{iteration + 1}.csv',
        mode='w+', header=True)
    del total_df


if __name__ == "__main__":
    csv_flow()