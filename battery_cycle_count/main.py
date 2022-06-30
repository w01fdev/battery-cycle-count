#!/usr/bin/env python3

"""Battery Cycle Count
Copyright (C) 2022 w01f - https://github.com/w01fdev/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

########################################################################

w01f hacks from Linux for Linux!

fck capitalism, fck patriarchy, fck racism, fck animal oppression...

########################################################################
"""

import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd


class Base:
    """Counts the battery cycles of a device.

    These are determined using the data of a <csv> file. Of course, the data
    should be recorded from the beginning, as soon as the device is used for
    the first time.

    I recorded the initial charge level with the date when I used the device
    for the first time.

    example for a <csv> file:
    date,battery_saver,start_percent,end_percent
    2022-03-29,0,0,70
    2022-04-02,1,25,50
    2022-04-06,1,29,50
    2022-04-09,1,30,50
    2022-04-12,1,34,60

    meaning of the columns:
    date:
        Date the device was charged. The first date is the standard charge from
        the manufacturer and was recorded on the day the device was first used.
        [date format: yyyy-mm-dd]
    battery_saver:
        Was the battery-saving mode on in the device? it doesn't matter how you
        configured the battery-saving mode, but whether this function was
        activated or not. Whether this was the case when the battery-saving
        mode was on all the time or only partially is up to you.
        [values: 0 - 1]
    start_percent:
        Percentage at which the device was connected to the charger.
        [values: 0 - 100]
    end_percent:
        Percentage at which the device was disconnected from the charger.
        [values: 0 - 100]

    battery saving mode are tracked to make it easier for pandas and possibly
    later for machine or deep learning to find correlations.
    """

    def __init__(self, file: str, delete_last_row: bool = True):
        """Initialization of the class.

        :param file: <str>
            path to file.
        :param delete_last_row: <bool> -> std: <True>
            Since the last row is not complete (days = nan), it is deleted by
            default. If the parameter is set to <False>, it is retained.
        """
        super().__init__()

        self._df = pd.read_csv(file, index_col=0, parse_dates=[0])
        self._file = file

        if delete_last_row:
            self._df.drop(self._df.tail(1).index, inplace=True)

        # create columns
        self._df['percent'] = (self._df['end_percent'] - self._df['start_percent'])
        self._df['days'] = self._create_column_days()

    def get_df(self) -> pd.DataFrame:
        """Returns the <Pandas.DataFrame>."""

        return self._df

    def get_file(self) -> str:
        """Returns the file path."""

        return self._file

    def set_file(self, file: str):
        """Sets the file path."""

        self._file = file

    def _create_column_days(self):
        """Creates the data for the <days> column in the <pandas.DataFrame>.

        :return: <list>
        """

        days = []

        for ix, date in enumerate(self._df.index):
            try:
                days.append((self._df.index[ix + 1] - self._df.index[ix]).days)
            except IndexError:
                days.append(np.nan)

        return days


class Cycles(Base):
    """"""

    def __init__(self, file: str):
        super().__init__(file)

    def get_cycle_count(self) -> float:
        """Returns the number of cycles."""

        return float(self._df['percent'].sum() / 100)

    def get_cycle_prediction(self, years: int = 1) -> float:
        """Returns the expected cycles for <x> years."""

        date = (datetime.date.today() + relativedelta(years=years) - datetime.date.today()).days
        return round(float(date - self.get_cycle_count()) * self.get_daily_cycle(), 2)

    def get_daily_cycle(self) -> float:
        """Returns the number of average cycles per day."""

        return round(self.get_cycle_count() / self.get_days(), 2)

    def get_days(self) -> int:
        """Returns the number of days since it was recorded."""

        return (self._df.iloc[-1].name - self._df.iloc[0].name).days

    def get_300_cycles_date(self) -> datetime.date:
        """Returns the date on which 300 cycles are expected to be over."""

        return datetime.date.today() + datetime.timedelta(days=self.get_300_cycles_days())

    def get_300_cycles_days(self) -> int:
        """Returns the number of days at which 300 cycles are expected to be over."""

        return int(self.get_300_cycles_remaining() / self.get_daily_cycle())

    def get_300_cycles_remaining(self) -> float:
        """Returns the remaining cycles up to 300 charges."""

        return round(float(300 - self.get_cycle_count()), 2)


def main():
    """Main function of the program."""


if __name__ == '__main__':
    main()
