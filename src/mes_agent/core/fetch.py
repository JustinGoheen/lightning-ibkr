# Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import os
import sys
from calendar import monthrange
from datetime import datetime as dt

import ib_insync as ib
import pandas as pd
from rich import print as rprint
from rich.progress import Progress

from mes_agent.utilities.front_month import EquityFutureFrontMonth


class FetchWork:
    """a custom LightningWork to fetch data from IBKR"""

    def __init__(
        self,
        market: str = "MES",
        expiry: str = EquityFutureFrontMonth.expiry,
        current_month: str = "04",
        duration: str = "1 D",
        bar_size: str = "5 secs",
        what_to_show: str = "Trades",
        use_rth: bool = True,
        local_host: str = "127.0.0.1",
        port: str = "7497",
        datadir: str = "data",
    ):
        # init the parent class
        # super().__init__(parallel=False, cache_calls=True)
        # create an TWS API object
        self._ib = ib.IB()
        # set data settings
        self.market = market
        self.expiry = expiry
        self.current_month = current_month
        self.duration = duration
        self.bar_size = bar_size
        self.what_to_show = what_to_show
        self.use_rth = use_rth
        self.datadir = datadir
        self.end_date_time = None
        # set API connection settings
        self.ib_host = local_host
        self.ib_port = port
        self.app_id = 1001
        # create the market contract that will be requested
        self._marketcontract = ib.Future(self.market, exchange="CME", lastTradeDateOrContractMonth=self.expiry)
        # create the dataframe that will store bars
        columns = ["date", "open", "high", "low", "close", "volume", "average", "barCount"]
        self._marketdata = pd.DataFrame(columns=columns)
        # connect to TWS
        self._ib.connect(self.ib_host, self.ib_port, self.app_id)

    def _futuresbars(self) -> pd.DataFrame:
        """requests historical bars and returns a dataframe"""

        _data = self._ib.reqHistoricalData(
            self._marketcontract,
            endDateTime=self.end_date_time,
            durationStr=self.duration,
            barSizeSetting=self.bar_size,
            whatToShow=self.what_to_show,
            useRTH=self.use_rth,
        )

        self._ib.sleep(5)  # let bars fill

        _data = ib.util.df(_data)

        return _data

    def _days_to_fetch(self) -> list:
        # make a list of days to retrieve
        days = []

        if int(self.current_month) == dt.today().month:
            endofrange = dt.today().day + 1
        else:
            endofrange = monthrange(dt.today().year, int(self.current_month))[1] + 1

        with Progress() as progress:
            task = progress.add_task("CREATING DAYS TO FETCH", total=len(range(endofrange)))
            for i in reversed(range(endofrange)):
                lastday = str(dt.today().year) + self.current_month + str(endofrange - 1)
                lastday = dt.strptime(lastday, "%Y%m%d").date()
                offset = datetime.timedelta(days=i)
                offsetday = lastday - offset
                tradingday = str(offsetday).replace("-", "")
                # the time in the IBKR is set to 00:00 of t+1 so we have to use
                # tuesday through saturday to get monday through friday
                # if weekday is tuesday through saturday and the month is in the
                # target month and the day is not the 1st of the month
                if (
                    (offsetday.weekday() >= 1)
                    and (offsetday.weekday() < 6)
                    and (offsetday.month == int(self.current_month))
                    and (offsetday.day != 1)
                ):
                    days.append(str(dt.strptime(tradingday, "%Y%m%d")).replace("-", ""))

                progress.advance(task)

        # account for end of month days that fall on a weekday and need end of month + 1
        if lastday.weekday() <= 5:
            offset = datetime.timedelta(days=1)
            offsetday = lastday + offset
            tradingday = str(offsetday).replace("-", "")
            days.append(str(dt.strptime(tradingday, "%Y%m%d")).replace("-", ""))

        return days

    def _fetch_data(self):
        # fetch data
        days = self._days_to_fetch()
        with Progress() as progress:
            task = progress.add_task("FETCHING DATA", total=len(days))
            for day in days:
                self.end_date_time = day
                _bars = self._futuresbars()
                self._marketdata = pd.concat([self._marketdata, _bars], ignore_index=True)
                progress.advance(task)

    def _prep_data_for_storage(self):
        # prep data for storage
        self._marketdata.set_index("date", inplace=True)
        self._marketdata.sort_index(inplace=True)

    def _store_data_locally(self):
        # create path names
        symbolpath = os.path.join(self.datadir, self._marketcontract.symbol)
        yearpath = os.path.join(symbolpath, self.expiry[:4])
        monthpath = os.path.join(yearpath, self.current_month)
        # create directories if they do not exist
        for dir in [self.datadir, symbolpath, yearpath, monthpath]:
            if not os.path.exists(dir):
                os.mkdir(dir)
        # create filepath name
        filepath = "".join([monthpath, os.sep, f"historical_{self.bar_size.replace(' ', '_')}_bars.pq"])
        # save dataframe as parquet file format
        self._marketdata.to_parquet(filepath)

    def run(self) -> None:
        """runs the LightningWork from a Lightning Flow"""
        rprint(f"[{dt.now().time()}] RUNNING")
        # run ops
        rprint(f"[{dt.now().time()}] FETCHING DATA")
        self._fetch_data()
        rprint(f"[{dt.now().time()}] PREPARING FOR STORAGE")
        self._prep_data_for_storage()
        rprint(f"[{dt.now().time()}] SAVING")
        self._store_data_locally()
        rprint(f"[{dt.now().time()}] STOPPING")
        self.stop()

    def stop(self):
        self._ib.disconnect()
        sys.exit()
