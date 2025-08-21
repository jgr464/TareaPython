import io
import zipfile

import matplotlib.pyplot as plt
import pandas as pd
import requests


class BiciEMT:

    def __init__(self, url: str):
        self._contenido = self.csv_from_zip(url).read()
        self.df = self.get_data(io.StringIO(self._contenido))

    @staticmethod
    def csv_from_zip(url: str):
        try:

            response = requests.get(url)
            response.raise_for_status()  # Lanza HTTPError si no es 2xx
        except requests.RequestException as e:
            raise ConnectionError(f"Error al conectar con el servidor de la EMT: {e}")

        # Leer el contenido del ZIP en memoria
        zip_bytes = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_bytes) as z:
            # Buscar archivos CSV dentro del ZIP
            csv_files = [f for f in z.namelist() if f.lower().endswith('.csv')]
            if not csv_files:
                raise ValueError("El archivo ZIP no contiene ningún fichero CSV.")

            # Abrir el primer CSV y envolverlo como TextIO
            csv_file = z.open(csv_files[0])
            print("El método se ejecutó correctamente\n")
            return io.TextIOWrapper(csv_file, encoding='utf-8')

    @staticmethod
    def get_data(csv_file):
        columnas_interes = [
            'idBike', 'fleet', 'trip_minutes', 'geolocation_unlock', 'address_unlock', 'unlock_date',
            'locktype', 'unlocktype', 'geolocation_lock', 'address_lock', 'lock_date',
            'station_unlock', 'unlock_station_name', 'station_lock', 'lock_station_name'
        ]

        # Cargar el DataFrame cumpliendo las condiciones:
        df = pd.read_csv(
            csv_file,
            sep=';',  # Separador ';' como en los archivos de EMT
            usecols=columnas_interes,  # Solo las columnas requeridas
            index_col='unlock_date',  # Índice: la fecha de desbloqueo
            parse_dates=['unlock_date', 'lock_date']  # Convertir columnas de fecha a tipo datetime
        )
        # Convertir índice a solo fecha (sin hora)
        df.index = df.index.date
        # Renombrar el índice a 'fecha'
        df.index.name = 'fecha'
        return df

    def day_time(self):
        return self.df['trip_minutes'].groupby(self.df.index).sum() / 60

    def graficar_uso_diario(self):
        horas = self.day_time()
        plt.figure(figsize=(12, 6))
        horas.plot(kind='bar')
        plt.title("Horas totales de uso por día")
        plt.xlabel("Fecha")
        plt.ylabel("Horas")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
