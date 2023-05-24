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
        remaining_days = ((remaining.total_seconds() / 60) / 720)
        # if remaining days is like integer (e.g. 1, 2, 3)

        if floor(remaining_days) == remaining_days:
            return remaining_days
        else:
            #if its not so we keep one extra iteration
            return floor(remaining_days) + 1


    def next(self):
        period = (self.endDate - self.currentRegionPointer).total_seconds()
        region_piece = None
        if 1 > (period / 60 / 720) > 0:
            region_piece = self.collector.collect(
                self.interval,
                startDate=self.currentRegionPointer,
                endDate=self.currentRegionPointer + timedelta(seconds=period)
            )
            self.currentRegionPointer += timedelta(seconds=period)
        else:
            print(self.currentRegionPointer, self.currentRegionPointer + timedelta(hours=12))
            region_piece = self.collector.collect(
                self.interval,
                startDate=self.currentRegionPointer,
                endDate=self.currentRegionPointer + timedelta(hours=12)
            )
            self.currentRegionPointer += timedelta(hours=12)

        return region_piece

