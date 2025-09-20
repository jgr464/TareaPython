import pandas as pd
from .UrlEMT import UrlEMT
import matplotlib.pyplot as plt

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
        self._data.index = self._data.index.normalize()
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

    def most_popular_stations(self) -> set:
        """
        Devuelve el conjunto de direcciones de las 3 estaciones de desbloqueo
        más utilizadas en el mes.

        Returns:
            set: Direcciones de las 3 estaciones más utilizadas.
        """
        counts = self._data['address_unlock'].value_counts()
        return set(counts.head(3).index)

    def day_time(self, plot: bool = False) -> pd.Series:
        """
        Calcula las horas totales de uso de bicicletas por día.

        Args:
            plot (bool): Si True, dibuja un gráfico de barras.

        Returns:
            pd.Series: Serie con índice = fechas y valores = horas de uso.
        """
        horas_por_dia = self._data.groupby(self._data.index)['trip_minutes'].sum() / 60

        if plot:
            horas_por_dia.plot(kind='bar', figsize=(12, 6))
            plt.title("Horas totales de uso de BiciMAD por día")
            plt.xlabel("Día")
            plt.ylabel("Horas de uso")
            plt.show()

        return horas_por_dia

    def weekday_time(self) -> pd.Series:
        """
        Calcula las horas totales de uso de bicicletas por día de la semana.

        Returns:
            pd.Series: Serie con índice = días de la semana (L, M, X, J, V, S, D)
                       y valores = horas de uso.
        """
        # Mapear número de día (0=lunes, 6=domingo) a letras
        dias = ["L", "M", "X", "J", "V", "S", "D"]
        weekday = self._data.index.to_series().map(lambda d: dias[d.weekday()])

        horas_por_dia = self._data.groupby(weekday)['trip_minutes'].sum() / 60

        # Reordenar para que aparezcan en orden de lunes a domingo
        horas_por_dia = horas_por_dia.reindex(dias, fill_value=0)

        return horas_por_dia

    def total_usage_day(self) -> pd.Series:
        """
        Calcula el número total de usos de bicicletas por día del mes.

        Returns:
            pd.Series: Serie con índice = fechas y valores = número de usos.
        """
        usos_por_dia = self._data.groupby(self._data.index).size()
        usos_por_dia.index.name = "fecha"
        usos_por_dia.name = "total_usos"
        return usos_por_dia

    def total_usage_by_station_day(self) -> pd.DataFrame:
        """
        Calcula el número total de usos por fecha y estación de desbloqueo.

        Returns:
            pd.DataFrame: DataFrame con MultiIndex (fecha, estación de desbloqueo)
                          y valores = número de usos.
        """
        usos = (
            self._data
            .groupby([pd.Grouper(freq="1D"), "station_unlock"])
            .size()
            .rename("total_usos")
        )
        return usos

    def usage_from_most_popular_station(self) -> pd.Series:
        """
        Devuelve el número de usos de las 3 estaciones de desbloqueo
        más populares en el mes.

        Returns:
            pd.Series: Serie con estaciones como índice y número de usos como valores.
        """
        counts = self._data['address_unlock'].value_counts()
        return counts.head(3)

