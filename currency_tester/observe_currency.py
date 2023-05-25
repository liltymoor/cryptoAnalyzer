import profile
import sys
sys.path.insert(1, '../')
from api_keys import API_KEY, SECRET_KEY
from datetime import datetime, timedelta
from sys import argv
from observe_constants import timeframes
import subprocess
from observe_flow_csv import combine_to_csv
from subprocess import Popen, PIPE
import gc
from dateutil.relativedelta import relativedelta


if argv[1] == "--help":
    print("python observe_currency.py <stock> <timeframe> <timestamp> <flows_num>")
    print("Example of using:\n\tpython observe_currency.py BTCUSDT 1m 1640984400 32")
    print()
    print("stock - currency that you want to test")
    print("timeframe - time interval for your currency")
    print("timestamp - time in timestamp format, that will be used as start point")
    print("flows_num - number of flows that will be collecting data from Binance_API")
    print()
    sys.exit()

stock = argv[1] # e.g 'BTCUSDT'
timeframe = argv[2] # e.g. '1m'
date_from = datetime.fromtimestamp(int(argv[3])) # Datetime in timestamp format
flow_count = int(argv[4]) # e.g. 16


def month_exporter(relative_date: datetime, current_month: int):
    date_to = relative_date + relativedelta(months=1)
    date_delta = (date_to - relative_date) / flow_count
    print(relative_date, date_to)
    start_pass = 78 * timeframes[timeframe]
    end_pass = 26 * timeframes[timeframe]

    header_status = 'True'
    subprocess_list = []

    # Getting Data
    for i in range(flow_count):

        csv = open(f'exported_info/csv/combine_tmp/Flow-{i}.csv', "w+")
        csv.close()

        if i != 0:
            process_start_date = relative_date + date_delta * i - start_pass + timeframes[timeframe]
        else:
            process_start_date = relative_date + date_delta * i - start_pass

        process_end_date = relative_date + date_delta * (i + 1) + end_pass

        process = subprocess.Popen(['python', "observe_flow_csv.py",
                                    stock, # stock
                                    process_start_date.isoformat(), # start date
                                    process_end_date.isoformat(), # end date
                                    timeframe, # timeframe
                                    str(i), # flow_number
                                    "backtest_strategy" # strategy name
                                    ])

        subprocess_list.append(process)

    for process in subprocess_list:
        process.communicate()

    for process in subprocess_list:
        process.terminate()

    del subprocess_list
    combine_to_csv(stock, current_month, flow_count)


def main():
    # Check data to be valid (at least 1 year ago)
    delta = datetime.now() - date_from
    if delta < timedelta(days=365):
        raise ValueError("date_from (3 argument) must be more than 1 year to observe it")

    relative_month = date_from
    for month in range(12):
        month_exporter(relative_month, month)
        relative_month = relative_month + relativedelta(months=1)
        gc.collect()


if __name__ == "__main__":
    main()
