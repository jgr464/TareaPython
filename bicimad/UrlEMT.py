import io
import re
import zipfile
from typing import TextIO, Set

import requests


class UrlEMT:
    EMT = 'https://opendata.emtmadrid.es/'
    GENERAL = "/Datos-estaticos/Datos-generales-(1)"

    def __init__(self):
        self._valid_urls = self.select_valid_urls()

    @staticmethod
    def get_links(html: str) -> Set[str]:
        # Expresión regular para encontrar todos los href con archivos CSV
        pattern = r'href=["\'](.*?trips_\d{2}_\d{2}_[A-Za-z]+\.csv)["\']'
        return set(re.findall(pattern, html))

    @staticmethod
    def select_valid_urls() -> Set[str]:
        url = UrlEMT.EMT + UrlEMT.GENERAL
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise ConnectionError("Fallo en la petición al servidor de la EMT")
            html = response.text
            links = UrlEMT.get_links(html)
            # Completar los enlaces parciales
            return {UrlEMT.EMT + link.lstrip('/') for link in links}
        except requests.RequestException as e:
            raise ConnectionError(f"Error al conectar con la EMT: {e}")

    def get_url(self, month: int, year: int) -> str:
        if not (1 <= month <= 12) or not (21 <= year <= 23):
            raise ValueError("Mes o año fuera de rango válido")

        # Formato trips_YY_MM_...csv
        prefix = f"trips_{year:02d}_{month:02d}_"
        for url in self._valid_urls:
            if prefix in url:
                return url
        raise ValueError("No existe un enlace válido para ese mes y año")

    def get_csv(self, month: int, year: int) -> TextIO:
        url = self.get_url(month, year)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Error al descargar el CSV: {e}")

        zip_bytes = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes) as z:
            csv_files = [f for f in z.namelist() if f.lower().endswith('.csv')]
            if not csv_files:
                raise ValueError("El ZIP no contiene archivos CSV")
            csv_file = z.open(csv_files[0])
            return io.TextIOWrapper(csv_file, encoding='utf-8')
