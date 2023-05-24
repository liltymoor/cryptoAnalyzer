import numpy as np
import pandas as pd

from ta import momentum
from ta import trend
from ta import volatility
from ta import volume
from ta import others




import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.expand_frame_repr = False





def fill_breakout_signals(data, main_list, low_value, high_value, name):
    main_list_prev = main_list.shift(1)

    # LONG
    buy_long_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev < low_value,
        main_list > low_value),
        main_list != main_list[0]), 1, 0)

    sell_long_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev > high_value,
        main_list < high_value),
        main_list != main_list[0]), 1, 0)

    # SHORT
    buy_short_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev > high_value,
        main_list < high_value),
        main_list != main_list[0]), 1, 0)

    sell_short_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev < low_value,
        main_list > low_value),
        main_list != main_list[0]), 1, 0)

    data[f'{name}_buy_long'] = buy_long_signals.copy()
    data[f'{name}_sell_long'] = sell_long_signals.copy()

    data[f'{name}_buy_short'] = buy_short_signals.copy()
    data[f'{name}_sell_short'] = sell_short_signals.copy()

    return data


def fill_cross_signals(data, main_list, signal_list, name):
    main_list_prev = main_list.shift(1)
    signal_list_prev = signal_list.shift(1)

    # LONG
    buy_long_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev < signal_list_prev,
        main_list > signal_list),
        main_list != main_list[0]), 1, 0)

    sell_long_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev > signal_list_prev,
        main_list < signal_list),
        main_list != main_list[0]), 1, 0)

    # SHORT
    buy_short_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev > signal_list_prev,
        main_list < signal_list),
        main_list != main_list[0]), 1, 0)

    sell_short_signals = np.where(np.logical_and(np.logical_and(
        main_list_prev < signal_list_prev,
        main_list > signal_list),
        main_list != main_list[0]), 1, 0)

    data[f'{name}_buy_long'] = buy_long_signals.copy()
    data[f'{name}_sell_long'] = sell_long_signals.copy()

    data[f'{name}_buy_short'] = buy_short_signals.copy()
    data[f'{name}_sell_short'] = sell_short_signals.copy()

    return data


def fill_ind_signals(data, first_list, second_list, name):
    data[f'{name}_buy_long'] = first_list.copy()
    data[f'{name}_sell_long'] = second_list.copy()

    data[f'{name}_buy_short'] = second_list.copy()
    data[f'{name}_sell_short'] = first_list.copy()

    return data


# Fill Data Functions
# MOMENTUM
def fill_ppo(data, return_df=None):
    ppo = momentum.PercentagePriceOscillator(close=data['Close'])

    ppo_df = ppo.ppo()
    ppo_signal_df = ppo.ppo_signal()
    if return_df is None:
        data = fill_cross_signals(data, ppo_df, ppo_signal_df, 'PPO')
        data['PPO'] = ppo_df.copy()
        data['PPO_SIGNAL'] = ppo_signal_df.copy()
    else:
        #result = pd.concat([return_df, ppo_df.copy(), ppo_signal_df], ignore_index=True)
        #result.rename(columns={'0': 'PPO', '1': 'PPO Signal'}, inplace= True)
        return_df['PPO'] = ppo_df
        return_df['PPO_SIGNAL'] = ppo_signal_df
        return return_df

    return data


def fill_rsi(data, return_df=None):
    rsi = momentum.RSIIndicator(close=data['Close'])

    rsi_df = rsi.rsi()
    if return_df is None:
        data = fill_breakout_signals(data, rsi_df, 30, 70, 'RSI')
        data['RSI'] = rsi_df.copy()
        return data
    else:
        #return_df['RSI'] = rsi_df['rsi']
        return_df['RSI'] = rsi_df

        return return_df


def fill_awesome_osc(data, return_df=None):
    awesome_osc = momentum.AwesomeOscillatorIndicator(high=data['High'], low=data['Low'])

    awesome_oscillator_df = awesome_osc.awesome_oscillator()

    if return_df is None:
        data = fill_breakout_signals(data, awesome_oscillator_df, 0, 0, 'Awesome_Osc')
        data['Awesome_Osc'] = awesome_oscillator_df.copy()
    else:
        return_df['RSI'] = awesome_oscillator_df.copy()



    return data


def fill_kama(data, return_df=None):
    kama = momentum.KAMAIndicator(close=data['Close'])

    if return_df is None:
        data['Kama'] = kama.kama().copy()
    else:
        return_df['Kama'] = kama.kama().copy()
    return data


def fill_pvo(data, return_df=None):
    pvo = momentum.PercentageVolumeOscillator(volume=data['Volume'])

    pvo_df = pvo.pvo()
    pvo_signal_df = pvo.pvo_signal()
    if return_df is None:
        data = fill_cross_signals(data, pvo_df, pvo_signal_df, 'PVO')
        data['PVO'] = pvo_df.copy()
        data['PVO_Signal'] = pvo_signal_df.copy()
        data['PVO_Hist'] = pvo.pvo_hist().copy()
    else:
        return_df['PVO'] = pvo_df.copy()
        return_df['PVO_Signal'] = pvo_signal_df.copy()
        return_df['PVO_Hist'] = pvo.pvo_hist().copy()



    return data

#TODO Заполнить до конца обработку на возвращаемый датафрейм.
def fill_roc(data, return_df=None):
    roc = momentum.ROCIndicator(close=data['Close'])

    roc_df = roc.roc()

    data['ROC'] = roc_df.copy()
    data = fill_breakout_signals(data, roc_df, 0, 0, 'ROC')

    return data


def fill_stochastic_osc(data):
    stoch_osc = momentum.StochasticOscillator(high=data['High'], low=data['Low'], close=data['Close'])

    data['Stoch'] = stoch_osc.stoch().copy()
    data['Stoch_Signal'] = stoch_osc.stoch_signal().copy()

    return data


def fill_stoch_rsi(data):
    stoch_rsi = momentum.StochRSIIndicator(close=data['Close'])

    data['Stoch_RSI'] = stoch_rsi.stochrsi().copy()
    data['Stoch_RSI_D'] = stoch_rsi.stochrsi_d().copy()
    data['Stoch_RSI_K'] = stoch_rsi.stochrsi_k().copy()

    return data


def fill_tsi(data):
    tsi = momentum.TSIIndicator(close=data['Close'])

    tsi_df = tsi.tsi()
    ttsi_signal_df = tsi_df.ewm(span=13, adjust=False).mean()

    data['TSI'] = tsi_df.copy()
    data['TSI_Signal'] = ttsi_signal_df.copy()

    data = fill_cross_signals(data, tsi_df, ttsi_signal_df, 'TSI')

    return data


def fill_ultimate_osc(data):
    ultimate_osc = momentum.UltimateOscillator(high=data['High'], low=data['Low'], close=data['Close'])

    data['Ulttmate_Osc'] = ultimate_osc.ultimate_oscillator().copy()

    return data


def fill_williams_r(data):
    williams_r = momentum.WilliamsRIndicator(high=data['High'], low=data['Low'], close=data['Close'])

    williams_r_df = williams_r.williams_r()

    data['Williams_R'] = williams_r_df.copy()

    data = fill_breakout_signals(data, williams_r_df, -80, -20, 'Williams_R')

    return data
# MOMENTUM end


# TREND
def fill_adx(data):
    adx = trend.ADXIndicator(low=data['Low'], high=data['High'], close=data['Close'])

    di_pos_df = adx.adx_pos()
    di_neg_df = adx.adx_neg()

    data['ADX'] = adx.adx().copy()
    data['DI+'] = di_pos_df.copy()
    data['DI-'] = di_neg_df.copy()

    data = fill_cross_signals(data, di_pos_df, di_neg_df, 'DI')

    return data


def fill_aroon(data):
    aroon = trend.AroonIndicator(data['Close'])

    aroon_down_df = aroon.aroon_down()
    aroon_up_df = aroon.aroon_up()

    data['AROON_UP'] = aroon_up_df.copy()
    data['AROON_DOWN'] = aroon_down_df.copy()

    data = fill_cross_signals(data, aroon_down_df, aroon_up_df, 'AROON')

    return data


def fill_cci(data):
    cci = trend.CCIIndicator(low=data['Low'], high=data['High'], close=data['Close'])

    cci_df = cci.cci()

    data['CCI'] = cci_df.copy()

    data = fill_breakout_signals(data, cci_df, -200, 200, 'CCI')

    return data


def fill_dpo(data):
    dpo = trend.DPOIndicator(data['Close'])

    dpo_df = dpo.dpo()

    data['DPO'] = dpo_df.copy()

    data = fill_breakout_signals(data, dpo_df, -0.04, 0.04, 'DPO')

    return data


def fill_ema(data):
    ema = trend.EMAIndicator(data['Close'])
    data['EMA'] = ema.ema_indicator().copy()

    return data


def fill_ichimoku(data):
    ichimoku = trend.IchimokuIndicator(high=data['High'], low=data['Low'])

    data['Ichimoku_Conversion'] = ichimoku.ichimoku_conversion_line().copy()
    data['Ichimoku_Base'] = ichimoku.ichimoku_base_line().copy()

    ichimoku_a_df = ichimoku.ichimoku_a()
    ichimoku_b_df = ichimoku.ichimoku_b()

    data['Ichimoku_SpanA'] = ichimoku_a_df.copy()
    data['Ichimoku_SpanB'] = ichimoku_b_df.copy()

    data = fill_cross_signals(data, ichimoku_a_df, ichimoku_b_df, 'Ichimoku')

    return data


def fill_kst(data):
    kst = trend.KSTIndicator(data['Close'])

    kst_df = kst.kst()
    kst_signal_df = kst.kst_sig()

    data['KST'] = kst_df.copy()
    data['KST_Signal'] = kst_signal_df.copy()
    data['KST_Diff'] = kst.kst_diff().copy()

    data = fill_cross_signals(data, kst_df, kst_signal_df, 'KST')

    return data


def fill_macd(data, return_df=None):
    macd = trend.MACD(data['Close'])

    macd_df = macd.macd()
    macd_signal_df = macd.macd_signal()
    if return_df is None:
        data['MACD'] = macd_df.copy()
        data['MACD_Signal'] = macd_signal_df.copy()
        data['MACD_Diff'] = macd.macd_diff()
        data = fill_cross_signals(data, macd_df, macd_signal_df, 'MACD')
    else:
        return_df['MACD'] = macd_df
        return_df['MACD_SIGNAL'] = macd_signal_df
        return_df['MACD_DIFF'] = macd.macd_diff()
        return return_df
    return data


def fill_massIndex(data):
    mi = trend.MassIndex(high=data['High'], low=data['Low'])

    mi_df = mi.mass_index()

    data['MI'] = mi_df.copy()

    data = fill_breakout_signals(data, mi_df, 8, 12, 'MI')

    return data


def fill_psar(data):
    psar = trend.PSARIndicator(high=data['High'], low=data['Low'], close=data['Close'])
    data['PSAR'] = psar.psar().copy()
    data['PSAR_UP'] = psar.psar_up().copy()
    data['PSAR_DOWN'] = psar.psar_down().copy()
    data['PSAR_UP_Ind'] = psar.psar_up_indicator().copy()
    data['PSAR_DOWN_Ind'] = psar.psar_down_indicator().copy()

    return data


def fill_sma(data, window=200):
    sma = trend.SMAIndicator(close=data['Close'], window=window)
    data['SMA'] = sma.sma_indicator().copy()

    return data


def fill_stc(data):
    stc = trend.STCIndicator(data['Close'])
    data['STC'] = stc.stc().copy()

    return data


def fill_trix(data):
    trix = trend.TRIXIndicator(data['Close'])

    trix_df = trix.trix()

    data['TRIX'] = trix_df.copy()

    data = fill_breakout_signals(data, trix_df, -8, 8, 'TRIX')

    return data


def fill_vortex(data):
    vortex = trend.VortexIndicator(close=data['Close'], high=data['High'], low=data['Low'])

    vortex_pos_df = vortex.vortex_indicator_pos()
    vortex_neg_df = vortex.vortex_indicator_neg()

    data['VORTEX+'] = vortex_pos_df.copy()
    data['VORTEX-'] = vortex_neg_df.copy()
    data['VORTEX_Diff'] = vortex.vortex_indicator_diff().copy()

    data = fill_cross_signals(data, vortex_pos_df, vortex_neg_df, 'VORTEX')

    return data


def fill_wma(data):
    wma = trend.WMAIndicator(data['Close'])
    data['WMA'] = wma.wma().copy()

    return data
# TREND end


# VOLATILITY
def fill_ATR(data):
    atr = volatility.AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'])
    data['ATR'] = atr.average_true_range().copy()

    return data


def fill_bollingerBands(data):
    bollinger = volatility.BollingerBands(data['Close'])
    data['Bollinger_AVG'] = bollinger.bollinger_mavg()

    bollinger_hband_ind_df = bollinger.bollinger_hband_indicator()
    bollinger_lband_ind_df = bollinger.bollinger_lband_indicator()

    data['Bollinger_HBand_Ind'] = bollinger_hband_ind_df.copy()
    data['Bollinger_LBand_Ind'] = bollinger_lband_ind_df.copy()

    data['Bollinger_HBAND'] = bollinger.bollinger_hband().copy()
    data['Bollinger_LBAND'] = bollinger.bollinger_lband().copy()
    data['Bollinger_BandPerc'] = bollinger.bollinger_pband().copy()
    data['Bollinger_BandWidth'] = bollinger.bollinger_wband().copy()

    data = fill_ind_signals(data, bollinger_hband_ind_df, bollinger_lband_ind_df, 'Bollinger')

    return data


def fill_donchian(data):
    donchian = volatility.DonchianChannel(high=data['High'], low=data['Low'], close=data['Close'])

    data['Donchian_High'] = donchian.donchian_channel_hband().copy()
    data['Donchian_Low'] = donchian.donchian_channel_lband().copy()
    data['Donchian_Center'] = donchian.donchian_channel_mband().copy()

    data['Donchian_BandWidth'] = donchian.donchian_channel_wband().copy()
    data['Donchian_BandPerc'] = donchian.donchian_channel_pband().copy()

    return data


def fill_keltner(data):
    keltner = volatility.KeltnerChannel(close=data['Close'], high=data['High'], low=data['Low'])

    data['Keltner_High'] = keltner.keltner_channel_hband().copy()
    data['Keltner_Low'] = keltner.keltner_channel_lband().copy()
    data['Keltner_Center'] = keltner.keltner_channel_mband().copy()

    data['Keltner_BandPerc'] = keltner.keltner_channel_pband().copy()
    data['Keltner_BandWidth'] = keltner.keltner_channel_pband().copy()

    keltner_channel_hband_ind_df = keltner.keltner_channel_hband_indicator()
    keltner_channel_lband_ind_df = keltner.keltner_channel_lband_indicator()

    data['Keltner_High_Ind'] = keltner_channel_hband_ind_df.copy()
    data['Keltner_Low_Ind'] = keltner_channel_lband_ind_df.copy()

    data = fill_ind_signals(data, keltner_channel_hband_ind_df, keltner_channel_lband_ind_df, 'Keltner')

    return data


def fill_ulcer(data):
    ulcer = volatility.UlcerIndex(data['Close'])
    data['Ulcer'] = ulcer.ulcer_index().copy()
    return data
# VOLATILITY end


# VOLUME
def fill_on_balance_volume(data):
    on_balance_volume = volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])

    on_balance_volume_df = on_balance_volume.on_balance_volume()
    on_balance_volume_signal_df = on_balance_volume_df.rolling(window=21).mean()

    data['OBV'] = on_balance_volume_df.copy()
    data['OBV_Signal'] = on_balance_volume_signal_df.copy()

    data = fill_cross_signals(data, on_balance_volume_df, on_balance_volume_signal_df, 'OBV')

    return data


def fill_acc_dist_index(data):

    acc_dist_index = volume.AccDistIndexIndicator(high=data['High'], low=data['Low'],
                                                  close=data['Close'], volume=data['Volume'])

    acc_dist_index_df = acc_dist_index.acc_dist_index()

    data['ADI'] = acc_dist_index_df.copy()

    data = fill_breakout_signals(data, acc_dist_index_df, 0, 0, 'ADI')

    return data


def fill_chaikin_mfi(data):
    chaikin_mfi = volume.ChaikinMoneyFlowIndicator(high=data['High'], low=data['Low'],
                                                  close=data['Close'], volume=data['Volume'])
    Chaikin_MFI_df = chaikin_mfi.chaikin_money_flow()

    data['Chaikin_MFI'] = Chaikin_MFI_df.copy()

    data = fill_breakout_signals(data, Chaikin_MFI_df, -0.4, 0.4, 'Chaikin_MFI')

    return data


def fill_ease_of_movement(data):
    ease_of_movement = volume.EaseOfMovementIndicator(high=data['High'], low=data['Low'],
                                                      volume=data['Volume'])

    data['EOM'] = ease_of_movement.ease_of_movement().copy()
    data['EOM_SMA'] = ease_of_movement.sma_ease_of_movement().copy()

    return data


def fill_force_index(data):
    force_index = volume.ForceIndexIndicator(close=data['Close'], volume=data['Volume'])

    force_index_df = force_index.force_index()

    data['Force_Index'] = force_index_df.copy()

    data = fill_breakout_signals(data, force_index_df, -200, 200, 'Force_Index')

    return data


def fill_mfi(data):
    mfi = volume.MFIIndicator(high=data['High'], low=data['Low'],
                              close=data['Close'], volume=data['Volume'])

    money_flow_index_df = mfi.money_flow_index()

    data['MFI'] = money_flow_index_df.copy()

    data = fill_breakout_signals(data, money_flow_index_df, 20, 80, 'MFI')

    return data


def fill_negative_volume_index(data):
    negative_volume_index = volume.NegativeVolumeIndexIndicator(close=data['Close'],
                                                                volume=data['Volume'])

    data['NVI'] = negative_volume_index.negative_volume_index().copy()

    return data


def fill_volume_price_trend(data):
    volume_price_trend = volume.VolumePriceTrendIndicator(close=data['Close'],
                                                          volume=data['Volume'])

    data['VPT'] = volume_price_trend.volume_price_trend().copy()

    return data


def fill_volume_weighted_average_price(data):
    volume_weighted_average_price = volume.VolumeWeightedAveragePrice(
        high=data['High'], low=data['Low'], close=data['Close'], volume=data['Volume'])

    data['VWAP'] = volume_weighted_average_price.volume_weighted_average_price().copy()

    return data
# VOLUME end


# OTHERS
def fill_dailyReturn(data):
    daily = others.DailyReturnIndicator(data['Close'])
    data['DailyReturn'] = daily.daily_return().copy()

    return data


def fill_dailyLogReturn(data):
    daily = others.DailyLogReturnIndicator(data['Close'])

    DailyLogReturn_df = daily.daily_log_return()

    data['DailyLogReturn'] = DailyLogReturn_df.copy()

    data = fill_breakout_signals(data, DailyLogReturn_df, -0.04, 0.04, 'DailyLogReturn')

    return data


def fill_cumulativeReturn(data):
    cumulutive = others.CumulativeReturnIndicator(data['Close'])

    cumulative_return_df = cumulutive.cumulative_return()

    data['Cumulutive'] = cumulative_return_df.copy()

    data = fill_breakout_signals(data, cumulative_return_df, 0, 0, 'Cumulutive')

    return data
# OTHERS end
