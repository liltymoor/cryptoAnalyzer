from datetime import *
from api_keys import SECRET_KEY, API_KEY
import indicators.ta_indicators_fill as ind

class Stock:
    def __init__(self):
        self.stock = 'ALICEUSDT'

    def __str__(self):
        return self.stock

    def change(self, new_stock):
        self.stock = new_stock


class Date:
    def __init__(self):
        self.date = 'live'

    def __str__(self):
        return self.date

    def change(self, new_date):
        self.date = new_date


class Timeframe:
    def __init__(self):
        self.timeframe = 'live'

    def __str__(self):
        return self.timeframe

    def change(self, new_tf):
        self.timeframe = new_tf


class FoldPath:
    def __init__(self):
        self.fold_path = \
            '.'.join(str(START_DATE).split(':')) \
            + '  —  ' \
            + '.'.join(str(END_DATE).split(':'))

    def __str__(self):
        return self.fold_path

    def change(self, new_path):
        self.fold_path = new_path


# class TableHeader:
#     def __init__(self):
#         self.header_status = True
#
#     def __bool__(self):
#         if self.header_status == 'True':
#             return True
#         else:
#             return False
#
#     def change(self, new_header_status):
#         self.header_status = new_header_status


class FlowNumber:
    def __init__(self):
        self.flow_number = '0'

    def __str__(self):
        return self.flow_number

    def __int__(self):
        return int(self.flow_number)

    def change(self, new_number):
        self.flow_number = new_number


class MonthNumber:
    def __init__(self):
        self.month_number = '1'

    def __str__(self):
        return self.month_number

    def change(self, new_number):
        self.month_number = new_number


class IsYearTest:
    def __init__(self):
        self.is_year_test = 'False'

    def __str__(self):
        return self.is_year_test

    def __bool__(self):
        if self.is_year_test == 'False':
            return False
        else:
            return True

    def change(self, new_value):
        self.is_year_test = new_value


class LiveCheck:
    def __init__(self):
        self.is_live = 'True'

    def __str__(self):
        return self.is_live

    def __bool__(self):
        if self.is_live == 'True':
            return True
        else:
            return False

    def change(self, new_value):
        self.is_live = new_value


class StrategyName:
    def __init__(self):
        self.name = 'backtest_strategy'

    def __str__(self):
        return self.name

    def change(self, new_name):
        self.name = new_name


class GlobalIterationNumber:
    def __init__(self):
        self.global_iteration_number = '0'

    def __str__(self):
        return self.global_iteration_number

    def change(self, new_numer):
        self.global_iteration_number = new_numer


class TotalCoef:
    def __init__(self):
        self.total_coef = 1

    def __float__(self):
        return float(self.total_coef)

    def __mul__(self, other_value):
        self.total_coef *= other_value

    def __imul__(self, other_value):
        self.total_coef *= other_value

    def change(self, new_value):
        self.total_coef = float(new_value)


# PRETTY COLORS
INDICATORS_COLORS = {
    'Blue': '#60B9CE',
    'Orange': '#FFB873',
    'Purple': '#AD66D5',
    'Emerald': '#5FD2B5',
    'Red': '#A60C00',
    'Green': '#007F16'
}


class Indicator:
    def __init__(self, name=None, attributes=None, levels=None):
        self.name = name
        self.attributes = attributes
        self.levels = levels

    def set(self, name=None, attributes=None, levels=None):
        self.name = name
        self.attributes = attributes
        self.levels = levels


# Indicators objects
# Momentum
ppo = Indicator(
    'PPO',                  # INDICATOR NAME
    ['PPO', 'PPO_Signal'],  # INDICATOR ATTRIBUTES
    []                      # INDICATOR LEVELS
)
rsi = Indicator('RSI', [['RSI', 'Red']], [[30, 70], [20, 80]])
awesome_osc = Indicator('Awesome OSC', ['Awesome_Osc'], [[0]])
kama = Indicator('Kama', ['Kama', 'Close'])
pvo = Indicator('PVO', ['PVO', 'PVO_Signal'])
roc = Indicator('ROC', ['ROC'], [[0]])
stochastic = Indicator('Stochastic OSC', ['Stoch', 'Stoch_Signal'])
stochastic_rsi = Indicator(
    'Stochastic RSI',
    [
        'Stoch_RSI',
        'Stoch_RSI_D',
        'Stoch_RSI_K'
    ])
tsi = Indicator('TSI', ['TSI', 'TSI_Signal'])
ultimate_osc = Indicator('Ultimate OSC', ['Ulttmate_Osc'], [30, 70])
william_r = Indicator('Williams R', ['Williams_R'], [-80, -20])


# Volatility
atr = Indicator('ATR', ['ATR'], [])
bollingerBand = Indicator(
    'Bollinger Band', [
        'Bollinger_AVG',
        'Bollinger_HBand_Ind',
        'Bollinger_LBand_Ind',
        'Bollinger_HBAND',
        'Bollinger_LBAND'], [])
donchian = Indicator('Donchian', [
        'Donchian_High',
        'Donchian_Low',
        'Donchian_Center'
        ], [])
keltner = Indicator('Keltner', [
        'Keltner_High',
        'Keltner_Low',
        'Keltner_Center',
        'Keltner_High_Ind',
        'Keltner_Low_Ind'
        ], [])
ulcer = Indicator('Ulcer', ['Ulcer'], [])

#VOLUME
obv = Indicator('On Balance Volume', ['OBV', 'OBV_Signal'], [])
adi = Indicator('Accumulation or Distribution Index (ADI)',
                ['ADI'], [])

INDICATORS_VOCABULARY_NAMES = {
    # Momentum
    'PPO': ['PPO', 'PPO_Signal'],
    'RSI': ['RSI'],
    'Awesome OSC': ['Awesome_Osc'],
    'Kama': ['Kama'],
    'PVO': ['PVO', 'PVO_Signal'],
    'ROC': ['ROC'],
    'Stochastic OSC': ['Stoch', 'Stoch_Signal'],
    'Stochastic RSI': [
        'Stoch_RSI',
        'Stoch_RSI_D',
        'Stoch_RSI_K'
    ],
    'TSI': ['TSI', 'TSI_Signal'],
    'Ultimate OSC': ['Ulttmate_Osc'],
    'Williams R': ['Williams_R'],

    # Trend
    'ADX': [
        'ADX',
        ['DI+', 'Green'],
        ['DI-', 'Red']
    ],
    'Aroon': ['AROON_UP', 'AROON_DOWN'],
    'CCI': ['CCI'],
    'DPO': ['DPO'],
    'EMA': ['EMA'],
    'Ichimoku': [
        'Ichimoku_Conversion',
        'Ichimoku_Base',
        ['Ichimoku_SpanA', 'Green'],
        ['Ichimoku_SpanB', 'Red']
    ],
    'KST': [
        'KST',
        'KST_Signal',
        'KST_Diff'
    ],
    'MACD': [
        'MACD',
        'MACD_Signal',
        'MACD_Diff'
    ],
    'Mass Index': ['MI'],
    'Parabolic SAR': [
        # 'PSAR',
        # 'Close',
        # 'PSAR_UP',
        # 'PSAR_DOWN',
        'PSAR_UP_Ind',
        'PSAR_DOWN_Ind'
    ],
    'SMA': ['SMA'],
    'STC': ['STC'],
    'TRIX': ['TRIX'],
    'VORTEX': [
        'VORTEX+',
        'VORTEX-'
        # 'VORTEX_Diff'
    ],
    'WMA': ['WMA'],

    #VOLATILITY
    'ATR': ['ATR'],
    'Bollinger Band': [
        # 'Bollinger_AVG',
        'Bollinger_HBand_Ind',
        'Bollinger_LBand_Ind',
        # 'Bollinger_HBAND',
        # 'Bollinger_LBAND',
        # 'Bollinger_BandPerc',
        # 'Bollinger_BandWidth',
    ],
    'Donchian': [
        'Donchian_High',
        'Donchian_Low',
        'Donchian_Center',
        'Donchian_BandWidth',
        'Donchian_BandPerc'
    ],
    'Keltner': [
        'Keltner_High',
        'Keltner_Low',
        'Keltner_Center',
        'Keltner_High_Ind',
        'Keltner_Low_Ind'
        #'Keltner_BandPerc',
        #'Keltner_BandWidth',
    ],
    'Ulcer': ['Ulcer'],

    #VOLUME
    'On Balance Volume': ['OBV', 'OBV_Signal'],
    'Accumulation or Distribution Index (ADI)': ['ADI'],
    'Chaikin MFI': ['Chaikin_MFI'],
    'Ease of Moment': ['EOM', 'EOM_SMA'],
    'Force Index': ['Force_Index'],
    'MFI': ['MFI'],
    'Negative Volume Index (NVI)': ['NVI'],
    'Volume Price Trend': ['VPT'],
    'Volume Weighted Average Price': ['VWAP'],

    #OTHERS
    'Daily Return': ['DailyReturn'],
    'Daily Log Return': ['DailyLogReturn'],
    'Cumulutive Return': ['Cumulutive']
}


INDICATORS_VOCABULARY = {
    # Momentum
    #TODO Заполнить ссылками на функции заполнения
    'PPO': [ind.fill_ppo, 'PPO', 'PPO_Signal'],
    'RSI': [ind.fill_rsi, 'RSI'],
    'Awesome OSC': [ind.fill_awesome_osc, 'Awesome_Osc'],
    'Kama': [ind.fill_kama, 'Kama'],
    'PVO': [ind.fill_pvo, 'PVO', 'PVO_Signal'],
    'ROC': [ind.fill_roc, 'ROC'],
    'Stochastic OSC': [ind.fill_stochastic_osc, 'Stoch', 'Stoch_Signal'],
    'Stochastic RSI': [ind.fill_stoch_rsi,
        'Stoch_RSI',
        'Stoch_RSI_D',
        'Stoch_RSI_K'
    ],
    'TSI': [ind.fill_tsi, 'TSI', 'TSI_Signal'],
    'Ultimate OSC': [ind.fill_ultimate_osc, 'Ulttmate_Osc'],
    'Williams R': [ind.fill_williams_r, 'Williams_R'],

    # Trend
    'ADX': [ind.fill_adx,
        'ADX',
        ['DI+', 'Green'],
        ['DI-', 'Red']
    ],
    'Aroon': [ind.fill_aroon, 'AROON_UP', 'AROON_DOWN'],
    'CCI': [ind.fill_cci, 'CCI'],
    'DPO': [ind.fill_dpo, 'DPO'],
    'EMA': [ind.fill_ema, 'EMA'],
    'Ichimoku': [ind.fill_ichimoku,
        'Ichimoku_Conversion',
        'Ichimoku_Base',
        ['Ichimoku_SpanA', 'Green'],
        ['Ichimoku_SpanB', 'Red']
    ],
    'KST': [ind.fill_kst,
        'KST',
        'KST_Signal',
        'KST_Diff'
    ],
    'MACD': [ind.fill_macd,
        'MACD',
        'MACD_Signal',
        'MACD_Diff'
    ],
    'Mass Index': [ind.fill_massIndex, 'MI'],
    'Parabolic SAR': [ ind.fill_psar,
        # 'PSAR',
        # 'Close',
        # 'PSAR_UP',
        # 'PSAR_DOWN',
        'PSAR_UP_Ind',
        'PSAR_DOWN_Ind'
    ],
    'SMA': [ind.fill_sma, 'SMA'],
    'STC': [ind.fill_stc, 'STC'],
    'TRIX': [ind.fill_trix, 'TRIX'],
    'VORTEX': [ind.fill_vortex,
        'VORTEX+',
        'VORTEX-'
        # 'VORTEX_Diff'
    ],
    'WMA': [ind.fill_wma, 'WMA'],

    #VOLATILITY
    'ATR': [ind.fill_ATR, 'ATR'],
    'Bollinger Band': [
        ind.fill_bollingerBands,
        # 'Bollinger_AVG',
        'Bollinger_HBand_Ind',
        'Bollinger_LBand_Ind',
        # 'Bollinger_HBAND',
        # 'Bollinger_LBAND',
        # 'Bollinger_BandPerc',
        # 'Bollinger_BandWidth',
    ],
    'Donchian': [
        ind.fill_donchian,
        'Donchian_High',
        'Donchian_Low',
        'Donchian_Center',
        'Donchian_BandWidth',
        'Donchian_BandPerc'
    ],
    'Keltner': [
        ind.fill_keltner,
        'Keltner_High',
        'Keltner_Low',
        'Keltner_Center',
        'Keltner_High_Ind',
        'Keltner_Low_Ind'
        #'Keltner_BandPerc',
        #'Keltner_BandWidth',
    ],
    'Ulcer': [ind.fill_ulcer, 'Ulcer'],

    #VOLUME
    'On Balance Volume': [ind.fill_on_balance_volume, 'OBV', 'OBV_Signal'],
    'Accumulation or Distribution Index (ADI)': [ind.fill_acc_dist_index,'ADI'],
    'Chaikin MFI': [ind.fill_chaikin_mfi, 'Chaikin_MFI'],
    'Ease of Moment': [ind.fill_ease_of_movement,'EOM', 'EOM_SMA'],
    'Force Index': [ind.fill_force_index, 'Force_Index'],
    'MFI': [ind.fill_mfi, 'MFI'],
    'Negative Volume Index (NVI)': [ind.fill_negative_volume_index, 'NVI'],
    'Volume Price Trend': [ind.fill_volume_price_trend, 'VPT'],
    'Volume Weighted Average Price': [ind.fill_volume_weighted_average_price, 'VWAP'],

    #OTHERS
    'Daily Return': [ind.fill_dailyReturn, 'DailyReturn'],
    'Daily Log Return': [ind.fill_dailyLogReturn,'DailyLogReturn'],
    'Cumulutive Return': [ind.fill_cumulativeReturn, 'Cumulutive']
}


INDICATORS = [
    ['Close'],
    # ['RSI'],
    # ['MFI'],
    # ['CCI'],
    # ['PSAR_UP_Ind', 'PSAR_DOWN_Ind'],
    # ['ADI'],
    # ['Bollinger_HBand_Ind', 'Bollinger_LBand_Ind'],
    # ['TSI', 'TSI_Signal'],
    # ['MACD', 'MACD_Signal'],
    # ['ADX'],
    # ['AROON_DOWN', 'AROON_UP'],
    # ['DI+', 'DI-']
]

CONDITIONS = ['Breakout', 'Cross', 'Ind', 'Stop']

MAX_COUNTS = 5

CONDITIONS_VOC_LONG = {
    # 'ADX': [['ADX'], CONDITIONS[0], 20],
    'DI': [['DI+', 'DI-'], CONDITIONS[1]],
    #'ATR'
    'ADI': [['ADI'], CONDITIONS[0], 0],
    'Aroon': [['AROON_DOWN', 'AROON_UP'], CONDITIONS[1]],
    'Awesome_Osc': [['Awesome_Osc'], CONDITIONS[0], 0],
    'Bollinger_Band': [
        ['Bollinger_HBand_Ind', 'Bollinger_LBand_Ind'],
        CONDITIONS[2]
    ],
    'CCI': [['CCI'], CONDITIONS[0], -200],

    'MACD': [['MACD', 'MACD_Signal'], CONDITIONS[1]]
}

CONDITIONS_VOC_SHORT = {
    # 'ADX': [['ADX'], CONDITIONS[0], 20],
    'DI': [['DI+', 'DI-'], CONDITIONS[1]],
    #'ATR'
    'ADI': [['ADI'], CONDITIONS[0], 0],
    'Aroon': [['AROON_DOWN', 'AROON_UP'], CONDITIONS[1]],
    'Awesome_Osc': [['Awesome_Osc'], CONDITIONS[0], 0],
    'Bollinger_Band': [
        ['Bollinger_HBand_Ind', 'Bollinger_LBand_Ind'],
        CONDITIONS[2]
    ],
    'CCI': [['CCI'], CONDITIONS[0], 200],

    'MACD': [['MACD', 'MACD_Signal'], CONDITIONS[1]]
}

CONDITIONS_VOC = {
    # 'ADX': [['ADX'], CONDITIONS[0], 20],
    'RSI': [['RSI'], CONDITIONS[0], [30, 70]],
    'DI': [['DI+', 'DI-'], CONDITIONS[1]],
    #'ATR'
    'ADI': [['ADI'], CONDITIONS[0], [0, 0]],
    'Aroon': [['AROON_DOWN', 'AROON_UP'], CONDITIONS[1]],
    'Awesome_Osc': [['Awesome_Osc'], CONDITIONS[0], [0, 0]],
    'Bollinger_Band': [
        ['Bollinger_HBand_Ind', 'Bollinger_LBand_Ind'],
        CONDITIONS[2]
    ],
    'CCI': [['CCI'], CONDITIONS[0], [-200, 200]],
    'Chaikin_MFI': [
        ['Chaikin_MFI'], CONDITIONS[0], [-0.4, 0.4]
    ],
    'Cumulutive_Return': [
        ['Cumulutive'], CONDITIONS[0], [0, 0]
    ],
    'DPO': [['DPO'], CONDITIONS[0], [-0.04, 0.04]],
    'Daily_Log_Return': [
        ['DailyLogReturn'], CONDITIONS[0], [-0.04, 0.04]
    ],
    'Force_Index': [['Force_Index'], CONDITIONS[0], [-200, 200]],
    # 'Daily_Return': [['DailyReturn']],
    # 'Donchian': [
    #     'Donchian_High',
    #     'Donchian_Low',
    #     'Donchian_Center'
    #     # 'Donchian_BandWidth',
    #     # 'Donchian_BandPerc',
    # ],

    'MACD': [['MACD', 'MACD_Signal'], CONDITIONS[1]],
    'MFI': [['MFI'], CONDITIONS[0], [20, 80]],
    'Parabolic_SAR': [
        ['PSAR_UP_Ind', 'PSAR_DOWN_Ind'], CONDITIONS[2]
    ],
    'PVO': [
        ['PVO', 'PVO_Signal'], CONDITIONS[1]
    ],
    'Williams_R': [
        ['Williams_R'], CONDITIONS[0], [-80, -20]
    ],
    'ROC': [
        ['ROC'], CONDITIONS[0], [0, 0]
    ],
    'VORTEX': [
        ['VORTEX+', 'VORTEX-'], CONDITIONS[1]
    ],
    'TSI': [
        ['TSI', 'TSI_Signal'], CONDITIONS[1]
    ],
    'Keltner': [
        ['Keltner_High_Ind', 'Keltner_Low_Ind'], CONDITIONS[2]
    ]
}

INDICATORS_SIGNALS_VOC = {
    'Aroon': [
        'AROON_buy_long', 'AROON_sell_long', 'AROON_buy_short', 'AROON_sell_short'
    ],
    'Awesome_Osc': [
        'Awesome_Osc_buy_long', 'Awesome_Osc_sell_long', 'Awesome_Osc_buy_short', 'Awesome_Osc_sell_short'
    ],
    'Bollinger_Band': [
        'Bollinger_buy_long', 'Bollinger_sell_long', 'Bollinger_buy_short', 'Bollinger_sell_short'
    ],
    'CCI': [
        'CCI_buy_long', 'CCI_sell_long', 'CCI_buy_short', 'CCI_sell_short'
    ],
    'Chaikin_MFI': [
        'Chaikin_MFI_buy_long', 'Chaikin_MFI_sell_long', 'Chaikin_MFI_buy_short', 'Chaikin_MFI_sell_short'
    ],
    'Cumulutive_Return': [
        'Cumulutive_buy_long', 'Cumulutive_sell_long', 'Cumulutive_buy_short', 'Cumulutive_sell_short'
    ],
    'Daily_Log_Return': [
        'DailyLogReturn_buy_long', 'DailyLogReturn_sell_long',
        'DailyLogReturn_buy_short', 'DailyLogReturn_sell_short'
    ],
    'DPO': [
        'DPO_buy_long', 'DPO_sell_long', 'DPO_buy_short', 'DPO_sell_short'
    ],
    'Force_Index': [
        'Force_Index_buy_long', 'Force_Index_sell_long', 'Force_Index_buy_short', 'Force_Index_sell_short'
    ],
    'Ichimoku': [
        'Ichimoku_buy_long', 'Ichimoku_sell_long', 'Ichimoku_buy_short', 'Ichimoku_sell_short'
    ],
    'Keltner': ['Keltner_buy_long', 'Keltner_sell_long', 'Keltner_buy_short', 'Keltner_sell_short'
    ],
    'KST': [
        'KST_buy_long', 'KST_sell_long', 'KST_buy_short', 'KST_sell_short'
    ],
    'MACD': [
        'MACD_buy_long', 'MACD_sell_long', 'MACD_buy_short', 'MACD_sell_short'
    ],
    'MI': [
        'MI_buy_long', 'MI_sell_long', 'MI_buy_short', 'MI_sell_short'
    ],
    'MFI': [
        'MFI_buy_long', 'MFI_sell_long', 'MFI_buy_short', 'MFI_sell_short'
    ],
    'On_Balance_Volume': [
        'OBV_buy_long', 'OBV_sell_long', 'OBV_buy_short', 'OBV_sell_short'
    ],
    'PPO': [
        'PPO_buy_long', 'PPO_sell_long', 'PPO_buy_short', 'PPO_sell_short'
    ],
    'PVO': [
        'PVO_buy_long', 'PVO_sell_long', 'PVO_buy_short', 'PVO_sell_short'
    ],
    'ROC': [
        'ROC_buy_long', 'ROC_sell_long', 'ROC_buy_short', 'ROC_sell_short'
    ],
    'RSI': [
        'RSI_buy_long', 'RSI_sell_long', 'RSI_buy_short', 'RSI_sell_short'
    ],
    'TRIX': [
        'TRIX_buy_long', 'TRIX_sell_long', 'TRIX_buy_short', 'TRIX_sell_short'
    ],
    'TSI': [
        'TSI_buy_long', 'TSI_sell_long', 'TSI_buy_short', 'TSI_sell_short'
    ],
    'VORTEX': [
        'VORTEX_buy_long', 'VORTEX_sell_long', 'VORTEX_buy_short', 'VORTEX_sell_short'
    ],
    'Williams_R': [
        'Williams_R_buy_long', 'Williams_R_sell_long', 'Williams_R_buy_short', 'Williams_R_sell_short'
    ]
}


START_DATE = Date()
# TIME_DELTA = timedelta(hours=6)
END_DATE = Date()
STOCK = Stock()
INTERVAL = Timeframe()
FOLD_PATH = FoldPath()
# TABLE_HEADER = TableHeader()
FLOW_NUMBER = FlowNumber()
MONTH_NUMBER = MonthNumber()
IS_YEAR_TEST = IsYearTest()
IS_LIVE = LiveCheck()
STRATEGY_NAME = StrategyName()
GLOBAL_ITERATION_NUMBER = GlobalIterationNumber()

TOTAL_COEF = TotalCoef()

INDICATOR_NAME = 'RSI'

BINANCE_LIMIT_COMM = 0.9998  # 0.999  # 0.99925
BINANCE_MARKET_COMM = 0.9996
# BINANCE_MARKET_COMM = 0.99977
SIGNALS_ACCURACY = 4


# EMA
EMA_LIST = [10, 40, 200]

# MACD
SHORT_MA = 12
LONG_MA = 26
MACD_SMOOTH = 9

# RSI
# RSI_PERIOD = 3
RSI_PERIOD = 14
RSI_OVERSOLD = 70
RSI_OVERBOUGHT = 30
RSI_MIDDLE = 50
RSI_CRITICAL_OVERBOUGHT = 80
RSI_CRITICAL_OVERSOLD = 20

# STOCH
STOCH_K_PERIOD = 14
STOCH_K_SMOOTHING = 3
STOCH_D_PERIOD = 3
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80

# S&R
SR_SELL = 0.7
SR_BUY = 0.3

# MFI
MFI_PERIOD = 14
MFI_OVERSOLD = 20
MFI_OVERBOUGHT = 80

# ISCHIMOKU
ISCHIMOKU_TS_PERIOD = 9
ISCHIMOKU_KS_PERIOD = 26
ISCHIMOKU_SSB_PERIOD = 52
ISCHIMOKU_DISPLACEMENT = 26

# CHAIKIN OSC
CHAIKIN_SHORT = 3
CHAIKIN_LONG = 10

# ADX
# ADX -DI +DI
# ADX_PERIOD = 5
ADX_PERIOD = 14
# ADX_20_LINE = 30
ADX_20_LINE = 25

# OBV
OBV_Signal_Period = 21

# TSI
TSI_Signal_Period = 13


DF_COLUMNS = [
    'Open Time',
    'Open',
    'High',
    'Low',
    'Close',
    'Volume',
    'Close Time',
    'Quote Asset Volume',
    'Number of Trades',
    'TB Base Volume',
    'TB Quote Volume',
    'Ignore'
]


DF_NUMERIC_COLUMNS = [
    'Open',
    'High',
    'Low',
    'Close',
    'Volume',
    'Quote Asset Volume',
    'TB Base Volume',
    'TB Quote Volume'
]

#-------------------------------
#-------------------------------
#-------------------------------

BOKEH_SUBWINDOW_CURSOR_RESIZE_PARAM = 5
BOKEH_SUBWINDOW_MINIMUM_WIDTH = 330
BOKEH_SUBWINDOW_MINIMUM_HEIGHT = 390


SELECTION_DIALOG_WIDTH = 402
SELECTION_DIALOG_HEIGHT = 284
