import os
import sqlite3
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

import constants
from constants import *




def load_data(start_date, end_date):    # Loading data columns
    return yf.download(str(STOCK), interval=str(INTERVAL), start=start_date, end=end_date)


def fill_data(data):            # Filling data columns
    data['EMA' + str(SHORT_MA)] = data.Close.ewm(span=SHORT_MA, adjust=False).mean()
    data['EMA' + str(LONG_MA)] = data.Close.ewm(span=LONG_MA, adjust=False).mean()
    macd = data['EMA' + str(SHORT_MA)] - data['EMA' + str(LONG_MA)]
    data['MACD'] = macd
    data['Signal Line'] = macd.ewm(span=MACD_SMOOTH, adjust=False).mean()

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

















