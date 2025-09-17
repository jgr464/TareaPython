import pandas as pd
from .UrlEMT import UrlEMT

class BiciMad:
    """
    Clase que representa los datos de uso del sistema BiciMAD durante un mes concreto.
    """

    def __init__(self, month: int, year: int):
        """
        Constructor de clase.

        Inicializa el objeto con el mes y el año indicados. Lanza una excepción si los valores están fuera de rango.
        Obtiene automáticamente el DataFrame de datos llamando al método estático `get_data`.

        Parámetros:
        - month (int): Mes entre 1 y 12.
        - year (int): Año entre 21 y 23 (representando 2021 a 2023).
        """
        if not (1 <= month <= 12 and 21 <= year <= 23):
            raise ValueError("Mes o año fuera de rango permitido.")
        self._month = month
        self._year = year
        self._data = self.get_data(month, year)

    @staticmethod
    def get_data(month: int, year: int) -> pd.DataFrame:
        """
        Método estático que descarga y devuelve el DataFrame con los datos de uso de bicicletas
        para el mes y año especificados. Solo se cargan las columnas necesarias y las fechas se
        parsean como datetime.

        Devuelve:
        - pd.DataFrame: DataFrame con los datos del CSV correspondiente.
        """
        enlaces = UrlEMT()
        csv_file = enlaces.get_csv(month, year)

        columnas = [
            'idBike', 'fleet', 'trip_minutes', 'geolocation_unlock', 'address_unlock', 'unlock_date',
            'locktype', 'unlocktype', 'geolocation_lock', 'address_lock', 'lock_date',
            'station_unlock', 'unlock_station_name', 'station_lock', 'lock_station_name'
        ]
        try:
            df = pd.read_csv(
                csv_file,
                sep=';',
                usecols=columnas,
                index_col='unlock_date',
                parse_dates=['unlock_date', 'lock_date']
            )
        except Exception as e:
            raise ValueError(f"Error al leer el CSV: {e}")

        return df

    @property
    def data(self):
        """
        Permite acceder directamente al DataFrame de datos de uso de bicicletas.

        Devuelve:
        - pd.DataFrame: DataFrame con los datos cargados.
        """
        return self._data

    def __str__(self):
        """
        Representación informal del objeto, muestra el contenido del DataFrame como string.

        Devuelve:
        - str: Representación en texto del DataFrame.
        """
        return str(self._data)

    def clean(self):
        """
        Limpia y transforma el DataFrame:
        - Elimina filas completamente vacías.
        - Convierte ciertas columnas a tipo string (fleet, idBike, station_unlock, station_lock).
        - Establece el índice como fecha (sin hora), con el nombre 'fecha'.
        """
        self._data.dropna(how='all', inplace=True)
        for col in ['fleet', 'idBike', 'station_lock', 'station_unlock']:
            self._data[col] = self._data[col].astype(str)
        self._data.index = self._data.index.date
        self._data.index.name = 'fecha'

    def resume(self) -> pd.Series:
        """
        Devuelve un resumen básico de los datos del mes:
        - Año y mes de los datos
        - Total de usos registrados
        - Tiempo total de uso en horas
        - Estación de desbloqueo más popular
        - Número de usos desde dicha estación

        Devuelve:
        - pd.Series: Resumen estadístico con la información indicada.
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
