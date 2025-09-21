import io
import re
import zipfile
from typing import TextIO, Set

import requests


class UrlEMT:
    """Clase que gestiona la obtención de enlaces válidos de uso de bicicletas eléctricas
    desde el portal de datos abiertos de la EMT de Madrid.

    Esta clase permite:
    - Obtener todos los enlaces válidos a archivos CSV comprimidos con datos de viajes.
    - Filtrar por mes y año.
    - Descargar y extraer el archivo CSV correspondiente a una fecha específica."""

    EMT = "https://antares.sip.ucm.es/"
    GENERAL = "luis/bicimad/"

    def __init__(self):
        """
        Inicializa la clase obteniendo el conjunto de enlaces válidos.
        """
        self._valid_urls = self.select_valid_urls()

    @staticmethod
    def get_links(html: str) -> Set[str]:
        """
        Toma como parámetros un texto HTML y devuelva un conjunto con todos los enlaces.
        Esta función usa expresiones regulares para encontrar los enlaces.

        Args:
            html (str): El texto HTML de la página.

        Returns:
            Set[str]: Un conjunto con los enlaces encontrados que coinciden con el patrón de los archivos CSV.
        """
        pattern = r'href=["\'](.*?trips_\d{2}_\d{2}_[A-Za-z]+-csv\.zip)["\']'
        return set(re.findall(pattern, html))

    @staticmethod
    def select_valid_urls() -> Set[str]:
        """
        Método estático que se encarga de actualizar el atributo de los objetos de la clase.
         Devuelve un conjunto de enlaces válidos. Si la petición al servidor de la EMT devuelve
         un código de retorno distinto de 200, la función lanza una excepción de tipo ConnectionError.

        Returns:
            Set[str]: Un conjunto de URLs válidas completas.

        Raises:
            ConnectionError: Si la petición al servidor falla o devuelve un código diferente de 200.
        """
        url = UrlEMT.EMT + UrlEMT.GENERAL
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise ConnectionError("Fallo en la petición al servidor de la EMT")
            html = response.text
            links = UrlEMT.get_links(html)
            return {url + link.lstrip('/') for link in links}
        except requests.RequestException as e:
            raise ConnectionError(f"Error al conectar con la EMT: {e}")

    def get_url(self, month: int, year: int) -> str:
        """
        Método de instancia que acepta los argumentos de tipo entero month y year y devuelve el string de
        la URL correspondiente al mes month y año year. Si no existe un enlace válido correspondiente al
        mes month y año year, se lanzará una excepción de tipo ValueError.


        Args:
            month (int): Mes del archivo (entre 1 y 12).
            year (int): Año del archivo (entre 21 y 23).

        Returns:
            str: La URL completa del archivo CSV.

        Raises:
            ValueError: Si el mes o el año están fuera del rango permitido, o si no existe un enlace para esa fecha.
        """
        if not (1 <= month <= 12) or not (21 <= year <= 23):
            raise ValueError("Mes o año fuera de rango válido")

        prefix = f"trips_{year:02d}_{month:02d}"
        for url in self._valid_urls:
            if prefix in url:
                return url
        raise ValueError("No existe un enlace válido para ese mes y año")

    def get_csv(self, month: int, year: int) -> TextIO:
        """
        Método de instancia que acepta los argumentos de tipo entero month y year y devuelve un fichero
        en formato CSV correspondiente al mes month y año year. El tipo del objeto devuelto es TextIO.
        La función lanza una excepción de tipo ConnectionError en caso de que falle la petición al servidor de la EMT.

        Args:
            month (int): Mes del archivo.
            year (int): Año del archivo.

        Returns:
            TextIO: Un objeto de texto con el contenido CSV.

        Raises:
            ConnectionError: Si falla la descarga del archivo ZIP.
            ValueError: Si el archivo ZIP no contiene un CSV.
        """
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
