import time

from PyQt6.QtCore import QObject
from PyQt6 import QtCore

import requests


from currency_handler import LiveCycler, CurrencyLiveCycle

class QPairFetcher(QObject):
    finished = QtCore.pyqtSignal(list)
    progress = QtCore.pyqtSignal(tuple)

    def fetch(self):
        response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
        response = response.json()
        response = response["symbols"]
        #TODO response for load bar
        #self.progress.emit(([], len(response)))
        pairs = []
        for pair in response:
            pairs.append(pair["symbol"])
            #self.progress.emit((len(pairs), len(response)))

        self.finished.emit(pairs)



class QBinanceDfFetcher(QObject):
    progress = QtCore.pyqtSignal(tuple)

    def __init__(self, client, pairs):
        super(QBinanceDfFetcher, self).__init__()
        self.cycler = LiveCycler(client, "", self.progress)
        self.currencies = pairs

    def start_fetching(self):
        while True:
            self.cycler.live_loop()
            time.sleep(self.cycler.interval_loop)

    def add_pair(self, pair: str, interval: str):
        self.cycler.add_currency(pair, interval)

    def get_currencies_list(self):
        return self.cycler.currencies
