import os
import sqlite3
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

import constants
from constants import *


def save_img(data):             # Signals
    # plt.figure()
    # plt.plot(data['EMA' + str(SHORT_MA)])
    # plt.plot(data['EMA' + str(LONG_MA)])
    # plt.savefig('Graphs/EMA.png')

    plt.figure()
    plt.plot(data['RSI'])
    plt.savefig('Graphs/rsi.png')

    plt.figure()
    plt.plot(data['S&R'])
    plt.savefig('Graphs/SnR.png')
    plt.cla()
    plt.clf()


def load_data(start_date, end_date):    # Loading data columns
    return yf.download(str(STOCK), interval=str(INTERVAL), start=start_date, end=end_date)


def fill_data(data):            # Filling data columns
    data['EMA' + str(SHORT_MA)] = data.Close.ewm(span=SHORT_MA, adjust=False).mean()
    data['EMA' + str(LONG_MA)] = data.Close.ewm(span=LONG_MA, adjust=False).mean()
    macd = data['EMA' + str(SHORT_MA)] - data['EMA' + str(LONG_MA)]
    data['MACD'] = macd
    data['Signal Line'] = macd.ewm(span=MACD_SMOOTH, adjust=False).mean()

    # plt.figure()
    # plt.plot(macd, label='DOGE MACD')
    # plt.plot(data['MACD'], label='Signal Line')
    # plt.legend(loc='upper left')
    # plt.savefig('Graphs/MACD.png')

    data['Return'] = data['Close'].pct_change()

    # data['Up'] = np.maximum(data['Close'].diff(), 0)
    # data['Down'] = np.maximum(-data['Close'].diff(), 0)
    #
    # data['RS'] = data['Up'].rolling(RSI_PERIOD).mean() / data['Down'].rolling(RSI_PERIOD).mean()
    # data['RSI'] = 100 - 100 / (1 + data['RS'])

    data['S&R'] = (data['Close'] / 10 ** np.floor(np.log10(data['Close']))) % 1

    data['MACD_signal'] = 2 * (data['EMA' + str(SHORT_MA)] > data['EMA' + str(LONG_MA)]) - 1
    # data['RSI_signal'] = 1 * (data['RSI'] < RSI_OVERSOLD) - 1 * (data['RSI'] > RSI_OVERBOUGHT)
    data['S&R_signal'] = 1 * (data['S&R'] < SR_BUY) - 1* (data['S&R'] > SR_SELL)
    return data


def make_graph(data):           # Making graph
    plt.figure()
    start = max(LONG_MA, RSI_PERIOD)

    buy_n_hold_return = np.array(data['Return'][start + 1:])
    macd_return = np.array(data['Return'][start + 1:]) * np.array(data['MACD_signal'][start:-1])
    # rsi_return = np.array(data['Return'][start + 1:]) * np.array(data['RSI_signal'][start:-1])
    snr_return = np.array(data['Return'][start + 1:]) * np.array(data['S&R_signal'][start:-1])

    buy_n_hold = np.prod(1 + buy_n_hold_return) ** (252 / len(macd_return))
    macd = np.prod(1 + macd_return) ** (252 / len(snr_return))
    # rsi = np.prod(1 + rsi_return) ** (252 / len(rsi_return))
    # snr = np.prod(1 + snr_return) ** (252 / len(snr_return))

    buy_n_hold_risk = np.std(buy_n_hold_return) * 252 ** 0.5
    macd_risk = np.std(macd_return) * 252 ** 0.5
    # rsi_risk = np.std(rsi_return) * 252 ** 0.5
    # snr_risk = np.std(snr_return) * 252 ** 0.5

    print('\n\t\tbuy-n-hold'
          + '\nДоходность: ' + str(round(buy_n_hold * 100, 2)) + '%'
          + '\nРиск: ' + str(round(buy_n_hold_risk * 100, 2)) + '%')
    print('\n\t\tEMA'
          + '\nДоходность: ' + str(round(macd * 100, 2)) + '%'
          + '\nРиск: ' + str(round(macd_risk * 100, 2)) + '%')
    # print('\n\t\tRSI'
    #       + '\nДоходность: ' + str(round(rsi * 100, 2)) + '%'
    #       + '\nРиск: ' + str(round(rsi_risk * 100, 2)) + '%')
    # print('\n\t\tS&R'
    #       + '\nДоходность: ' + str(round(snr * 100, 2)) + '%'
    #       + '\nРиск: ' + str(round(snr_risk * 100, 2)) + '%')

    plt.plot(np.cumprod(1 + buy_n_hold_return))
    plt.plot(np.cumprod(1 + macd_return))
    # plt.plot(np.cumprod(1 + rsi_return))
    # plt.plot(np.cumprod(1 + snr_return))

    plt.savefig('Graphs/graphs.png')
    plt.cla()
    plt.clf()


def buy_sell_rsi_test(data):
    buy = {
        'RSI': []
    }
    sell = {
        'RSI': []
    }

    upper_bought_1 = False
    lower_sold_1 = False

    upper_bought_2 = False
    lower_sold_2 = False

    upper_centre = False
    lower_centre = False

    centre = 50

    overbought_1 = 70
    oversold_1 = 30

    overbought_2 = 80
    oversold_2 = 20

    values = data['RSI']

    # Getting signal
    for i in range(len(data)):
        value = values[i]

        if upper_centre:
            if upper_bought_1:
                if upper_bought_2:
                    if value < overbought_2:
                        sell['RSI'].append([data['Close'], '2'])
                        buy['RSI'].append(np.nan)
                        upper_bought_2 = False
                        continue
                else:
                    if value < overbought_1:
                        sell['RSI'].append([data['Close'], '1'])
                        buy['RSI'].append(np.nan)
                        upper_bought_1 = False
                        continue
            else:
                if value < centre:
                    sell['RSI'].append([data['Close'], '0'])
                    buy['RSI'].append(np.nan)
                    upper_centre = False
                    continue

        if lower_centre:
            if lower_sold_1:
                if lower_sold_2:
                    if value > oversold_2:
                        buy['RSI'].append([data['Close'], '2'])
                        sell['RSI'].append(np.nan)
                        lower_sold_2 = False
                        continue
                else:
                    if value > oversold_1:
                        buy['RSI'].append([data['Close'], '1'])
                        sell['RSI'].append(np.nan)
                        lower_sold_1 = False
                        continue
            else:
                if value > centre:
                    buy['RSI'].append([data['Close'], '0'])
                    sell['RSI'].append(np.nan)
                    lower_centre = False
                    continue

        if value > centre:
            upper_centre = True
            if value > overbought_1:
                upper_bought_1 = True
                if value > overbought_2:
                    upper_bought_2 = True

        elif value < centre:
            lower_centre = True
            if value < oversold_1:
                lower_sold_1 = True
                if value < oversold_2:
                    lower_sold_2 = True

        sell['RSI'].append(np.nan)
        buy['RSI'].append(np.nan)

    return [buy, sell]


def buy_sell_rsi(data):
    buy = {
        'RSI': []
    }
    sell = {
        'RSI': []
    }
    stop_loss_voc = {
        'RSI': []
    }
    auto_buy_voc = {
        'RSI': []
    }

    upper_than_overbought = False
    lower_than_oversold = False

    overbought = RSI_OVERBOUGHT
    oversold = RSI_OVERSOLD

    last_rsi_ema_value = 0

    values = data['RSI']

    stop_loss = 0.005

    can_buy = True

    need_to_sell = False
    waiting_after_stop_loss = False

    reverse_50_signals = [False, False]
    await_center_reverse = False
    lower_than_50 = False

    can_sell = False
    last_sell = 0

    can_buy = False
    last_buy = 0
    in_deal = False
    need_to_buy = False
    auto_buy = 0.002

    can_buy_after_rsi_signal = False
    is_stop_loss_signal = False
    is_auto_buy = False

    value_before_buy = 0
    before_value = 0.001

    in_sell = False
    sell_change_value = 0.002

    # Getting signal
    for i in range(len(data)):
        value = values[i]
        # print(value)
        sell['RSI'].append(np.nan)
        buy['RSI'].append(np.nan)
        stop_loss_voc['RSI'].append(np.nan)
        auto_buy_voc['RSI'].append(np.nan)

        # if await_center_reverse:
        #     lower_than_50

        # Почти рабочий
        # # if last_buy != 0:
        # #     if can_sell:
        # #         if 1 - data['Close'][i] / last_buy >= stop_loss:
        # #             # print('РАБОТАЕТ')
        # #             is_stop_loss_signal = True
        # #             need_to_sell = True
        # #             can_buy_after_rsi_signal = False

        # if need_to_sell:
        #     if 1 - data['Close'][i] / last_buy >= stop_loss:
        #         sell['RSI'][i] = data['Close'][i]
        #         need_to_sell = False
        #         can_buy = False
        #         need_to_buy = True
        #         value_before_buy = data['Close'][i]

        # Почти рабочий
        # # if upper_than_overbought:
        # #     if value < overbought:
        # #         is_stop_loss_signal = False
        # #         need_to_sell = True
        # #         can_buy_after_rsi_signal = True
        # #
        # # if need_to_sell:
        # #     if is_stop_loss_signal:
        # #         stop_loss_voc['RSI'][i] = data['Close'][i]
        # #     else:
        # #         sell['RSI'][i] = data['Close'][i]
        # #
        # #     can_buy = True
        # #     last_sell = data['Close'][i]
        # #     need_to_sell = False
        # #     can_sell = False
        # #     in_deal = False
        # STOP-LOSS
        # if last_buy != 0:
        #     if 1 - data['Close'][i] / last_buy >= stop_loss:
        #         need_to_sell = True
        #         waiting_after_stop_loss = True

        if upper_than_overbought:
            if value < overbought:
                sell['RSI'][i] = data['Close'][i]
                need_to_sell = True
                waiting_after_stop_loss = False

        # if need_to_sell:
        #     sell['RSI'][i] = data['Close'][i]
        #     need_to_sell = False
        #     last_buy = 0
        #     # print('SELL =>', data['Close'][i])
        #     # print(data['_sign'][i], data['Signal Line'][i], '\n')
        #     await_center_reverse = True

        if lower_than_oversold:
            if value > oversold:
                # if not waiting_after_stop_loss:
                buy['RSI'][i] = data['Close'][i]
                last_buy = data['Close'][i]
                    # print('BUY =>', data['Close'][i])
                    # print(data['MACD'][i], data['Signal Line'][i])




        # if in_sell:
        #     if 1 - data['Close'][i] / last_sell >= sell_change_value:
        #         sell['RSI'][i] = data['Close'][i]
        #         need_to_sell = False
        #         can_buy = True
        #         in_sell = False
        #         last_sell = data['Close'][i]
        #         need_to_buy = True
        #         value_before_buy = data['Close'][i]

        # Почти рабочий
        #
        # # if lower_than_oversold:
        # #     if value > oversold:
        # #         if can_buy_after_rsi_signal:
        # #             need_to_buy = True
        # #             is_auto_buy = False
        # #             # if can_buy:
        # #             # print(values[i - 1])
        # #             lower_than_oversold = False
        # #             # need_to_sell = True
        # #
        # # if can_buy:
        # #     if 1 - last_sell / data['Close'][i] > auto_buy:
        # #         need_to_buy = True
        # #         is_auto_buy = True
        # #
        # # if need_to_buy:
        # #     if not in_deal:
        # #         if is_auto_buy:
        # #             auto_buy_voc['RSI'][i] = data['Close'][i]
        # #         else:
        # #             buy['RSI'][i] = data['Close'][i]
        # #
        # #         last_buy = data['Close'][i]
        # #         can_sell = True
        # #         can_buy = False
        # #
        # #         in_deal = True
        # #
        # #         need_to_buy = False


        # if need_to_buy:
        #     if 1 - value_before_buy / data['Close'][i] >= before_value:
        #         print(values[i - 1])
        #         buy['RSI'][i] = data['Close'][i]
        #         lower_than_oversold = False
        #         last_buy = data['Close'][i]
        #         need_to_sell = True
        #         need_to_buy = False
        upper_than_overbought = value > overbought
        lower_than_oversold = value < oversold

        # lower_than_50 = value < 50
        # upper_than_50 = value > 50

    # print(len(buy['RSI']))

    # return [buy, sell, auto_buy_voc, stop_loss_voc]
    # print(len([sell['RSI'][i] for i in range(len(sell['RSI'])) if str(sell['RSI'][i]) != 'nan']))
    return [buy, sell]


def buy_sell(data, ind_names):
    buy = {}
    sell = {}

    indicators = {
        'EMA': ['EMA' + str(SHORT_MA), 'EMA' + str(LONG_MA)],
        'MACD': ['MACD', 'Signal Line']
    }

    for ind_name in ind_names:
        indicator = indicators[ind_name]

        list_1 = data[indicator[0]]
        list_2 = data[indicator[1]]

        sell[ind_name] = []
        buy[ind_name] = []

        flag = -1

        # Getting signals
        for i in range(len(data)):
            if list_1[i] > list_2[i]:
                sell[ind_name].append(np.nan)
                if flag != 1:
                    buy[ind_name].append(data['Close'][i])
                    flag = 1
                else:
                    buy[ind_name].append(np.nan)
            elif list_1[i] < list_2[i]:
                buy[ind_name].append(np.nan)
                if flag != 0:
                    sell[ind_name].append(data['Close'][i])
                    flag = 0
                else:
                    sell[ind_name].append(np.nan)
            else:
                buy[ind_name].append(np.nan)
                sell[ind_name].append(np.nan)

    return [buy, sell]


def save_stats(data, ind_names, is_need_to_clear=False):
    file = open('../binance_information/Stats/' + str(STOCK) + ' stats.txt', 'w')

    flag = False

    total_coef = 1.0

    db_name = str(STOCK) + '-' + INDICATOR_NAME

    # print(data.head())
    start_date = data['Open Time']
    print(start_date[0][:-10])

    # print(FOLD_PATH)

    if bool(IS_YEAR_TEST):
        conn = sqlite3.connect(f'../TelegramBot/data/autotest/year_info.db')
    else:
        conn = sqlite3.connect(f'../binance_information/db/{str(INTERVAL)}/{str(FOLD_PATH)}/{db_name}.db')
    # print(INTERVAL)
    cur = conn.cursor()

    if is_need_to_clear:
        cur.execute('DELETE FROM Operations')

    for ind_name in ind_names:

        money = 100  # Start money ($USD)
        amount = 0  # Assets amount
        operations_count = 0

        buy_long = list(data[ind_name + '_Long_Buy_Signal'])
        sell_long = list(data[ind_name + '_Long_Sell_Signal'])

        buy_short = list(data[ind_name + '_Short_Buy_Signal'])
        sell_short = list(data[ind_name + '_Short_Sell_Signal'])

        # print(sell_short)
        # auto_buy = data[ind_name + '_Auto_Buy']
        # stop_loss = data[ind_name + '_Stop_Loss']

        sell_value = 0
        buy_value = 0

        if flag:
            file.write('\n\n-----------------------------------------------\n\n')
        else:
            flag = True

        file.write('\t\t\t' + ind_name + ' ' + str(STOCK) + ' Strategy\n\n' +
                   'Start money = $' + str(round(money, 2)) +
                   '\n\nAction\tPrice\t\t\tAmount\t\t\tMoney\n')

        can_execute = False
        is_long = False

        flag_1 = False
        flag_2 = False

        buy_price = 0
        sell_price = 0

        for i in range(len(buy_long)):
            if money != 0:
                # if str(buy[i]) != 'nan' or str(auto_buy[i]) != 'nan':
                #     if str(auto_buy[i]) != 'nan':
                #         buy_value = auto_buy[i]
                #     else:
                #         buy_value = buy[i]
                if str(buy_long[i]) != 'nan':
                    buy_value = buy_long[i]
                    amount = money / buy_value
                    money = 0
                    file.write('\nBUY->\t' +
                               str(round(buy_value, 5)) + '\t\t' +
                               str(round(amount, 8)) + '\t\t' +
                               str(round(money, 2)))
                    operations_count += 1
                    if not flag_1:
                        flag_1 = True
                        buy_price = buy_value

                if str(buy_short[i]) != 'nan':
                    buy_value = buy_short[i]
                    amount = money / buy_value
                    money = 0

                    if not flag_2:
                        flag_2 = True
                        buy_price = buy_value

            if amount != 0:
                # if str(sell[i]) != 'nan' or str(stop_loss[i]) != 'nan':
                #     if str(stop_loss[i]) != 'nan':
                #         sell_value = stop_loss[i]
                #     else:
                #         sell_value = sell[i]
                if str(sell_long[i]) != 'nan':
                    sell_value = sell_long[i]
                    money = amount * sell_value
                    amount = 0
                    file.write('\nSELL->\t' +
                               str(round(sell_value, 5)) + '\t\t' +
                               str(round(amount, 8)) + '\t\t\t\t' +
                               str(round(money, 2)))
                    operations_count += 1
                    if flag_1:
                        can_execute = True
                        is_long = True
                        flag_1 = False
                        sell_price = sell_value

                if str(sell_short[i]) != 'nan':
                    sell_value = sell_short[i]
                    money = amount * sell_value
                    amount = 0

                    if flag_2:
                        can_execute = True
                        is_long = False
                        flag_2 = False
                        sell_price = sell_value

            if can_execute:
                if is_long:
                    # print(str(data.index))
                    # print(buy_price, sell_price)
                    coef = round(sell_price / buy_price * BINANCE_MARKET_COMM
                                 * BINANCE_MARKET_COMM, 5)
                    total_coef *= coef

                    cur.execute(f'''INSERT INTO Operations VALUES (
                                {int(data.index[i])},'{start_date[i][:-10]}',
                                {buy_price},{sell_price},{coef})''')
                    can_execute = False
                    # print(buy_price, sell_price)
                else:
                    coef = round((1 + (1 - sell_price / buy_price)) * BINANCE_MARKET_COMM
                                 * BINANCE_MARKET_COMM, 5)
                    total_coef *= coef

                    cur.execute(f'''INSERT INTO Operations VALUES (
                                {int(data.index[i])},'{start_date[i][:-10]}',
                                {buy_price},{sell_price},{coef})''')
                    can_execute = False

        file.write('\n\nOperation count = ' + str(operations_count) +
                   '\nEnd money = $' + str(round(money, 2)))

    # cur.execute(f'''INSERT INTO Operations VALUES ('TOTAL',0,0,{round(total_coef, 3)})''')
    print(total_coef)

    constants.TOTAL_COEF.change(total_coef)
    # total_file = open('../TelegramBot/data/autotest/current_total.txt', 'w+')
    # total_file.write(str(total_coef))
    # total_file.close()

    file.close()
    conn.commit()
    conn.close()


def sql_connection(data):
    db_name = str(STOCK) + '-' + INDICATOR_NAME
    conn = sqlite3.connect('db/' + db_name + '.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO Operations VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
    conn.commit()
    conn.close()


def scan_stats():
    value = 1

    with open('psevdo-stats.txt', encoding='utf-8') as file:
        for line in file:
            value = value * float(line)
    file.close()
    print(value)
