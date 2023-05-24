from datetime import datetime

from PyQt6.QtCore import QObject
from PyQt6 import QtCore
import requests
import asyncio

from data.currency_handler import LiveCycler, CurrencyLiveCycle

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

    def __init__(self, client):
        super(QBinanceDfFetcher, self).__init__()
        self.cycler = LiveCycler(client, "", self.progress)

    @staticmethod
    def debug_msg(*msg):
        print("[BINANCE_CONNECTION]", ' '.join([str(i) for i in msg]))



    async def __loop(self):
        await self.cycler.setup_async_session()

        while True:
            await self.cycler.live_loop()
            await asyncio.sleep(self.cycler.interval_loop)


    def start_fetching(self):
        asyncio.run(self.__loop())

    def add_pair(self, pair: str, interval: str,
                 date_from: datetime = None,
                 date_to: datetime = None):
        # this one passes the currency from creator to sender
        currency = self.cycler.add_currency(pair, interval,
                                            date_from=date_from, date_to=date_to)
        print()
        QBinanceDfFetcher.debug_msg("Pair", currency.currency_pair, "were added. New list of pairs:")
        QBinanceDfFetcher.debug_msg("List:", [pair.currency_pair for pair in self.cycler.currencies])

        return currency

    def remove_pair(self, currency: CurrencyLiveCycle):
        counter = -1
        for pair in self.cycler.currencies:
            counter += 1
            if currency is pair:
                del self.cycler.currencies[counter]
        print()
        QBinanceDfFetcher.debug_msg("Pair", currency.currency_pair, "were removed. New list of pairs:")
        QBinanceDfFetcher.debug_msg([pair.currency_pair for pair in self.cycler.currencies])

    def get_currencies_list(self):
        return self.cycler.currencies
