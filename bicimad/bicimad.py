import pandas as pd

from UrlEMT import UrlEMT


class BiciMad:
    """BiciMad."""

    def __init__(self, month: int, year: int):
        """__init__.

        :param month:
        :type month: int
        :param year:
        :type year: int
        """
        self._month = month
        self._year = year
        self._data = self.get_data(month, year)

    @staticmethod

    def get_data(month: int, year: int) -> pd.DataFrame:
        """"""
        enlaces = UrlEMT()
        csv_file = enlaces.get_csv(month, year)

        columnas = [
            'idBike', 'fleet', 'trip_minutes', 'geolocation_unlock', 'address_unlock', 'unlock_date',
            'locktype', 'unlocktype', 'geolocation_lock', 'address_lock', 'lock_date',
            'station_unlock', 'unlock_station_name', 'station_lock', 'lock_station_name'
        ]

        df = pd.read_csv(
            csv_file,
            sep=';',
            usecols=columnas,
            index_col='unlock_date',
            parse_dates=['unlock_date', 'lock_date']
        )

        return df

    @property
    def data(self):
        """data."""
        return self._data

    def __str__(self):
        """__str__."""
        return str(self._data)

    def clean(self):
        """clean."""
        self._data.dropna(how='all', inplace=True)
        for col in ['fleet', 'idBike', 'station_lock', 'station_unlock']:
            self._data[col] = self._data[col].astype(str)
        self._data.index = self._data.index.date
        self._data.index.name = 'fecha'

    def resume(self) -> pd.Series:
        """resume.

        :rtype: pd.Series
        """
        total_uses = len(self._data)
        total_time = self._data['trip_minutes'].sum() / 60
        popular_counts = self._data['address_unlock'].value_counts()
        max_count = popular_counts.iloc[0]
        most_popular = set(popular_counts[popular_counts == max_count].index)

        return pd.Series({
            'year': self._year,
            'month': self._month,
            'total_uses': total_uses,
            'total_time': total_time,
            'most_popular_station': most_popular,
            'uses_from_most_popular': max_count
        })
