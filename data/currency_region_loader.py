import pickle
import sys

from binance_imports import Client
from table_imports import *

from datetime import *

from math import floor

class RegionController:
    def __init__(self, collector, interval, startDate: datetime, endDate: datetime,):
        self.startDate = startDate
        self.endDate = endDate

        self.interval = interval
        self.collector = collector

        self.currentRegionPointer = self.startDate


    #get the number of iterations to fully complete the region
    def get_remaining(self):
        remaining = self.endDate - self.currentRegionPointer
        # converting remaining time to days
        remaining_days = ((remaining.total_seconds() / 60) / 1000)
        # if remaining days is like integer (e.g. 1, 2, 3)

        if floor(remaining_days) == remaining_days:
            return remaining_days
        else:
            #if its not so we keep one extra iteration
            return floor(remaining_days) + 1

    def get_df_piece(self, start_date, end_date):
        period = (end_date - start_date).total_seconds()

        if 1 > (period / 60 / 1000) > 0:
            region_piece = self.collector.collect(
                self.interval,
                startDate=start_date,
                endDate=start_date + timedelta(seconds=period)
            )

        else:

            region_piece = self.collector.collect(
                self.interval,
                startDate=start_date,
                endDate=start_date + timedelta(hours=16, minutes=40)
            )

        return region_piece
