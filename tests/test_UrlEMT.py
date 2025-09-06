import re
from unittest.mock import patch, Mock
import pytest
from bicimad.UrlEMT import UrlEMT

# HTML de prueba simulado
html_sample = '''
<html>
    <body>
        <a href="files/trips_23_06_June.csv">Junio</a>
        <a href="files/trips_22_12_December.csv">Diciembre</a>
        <a href="otherfile.pdf">Otro archivo</a>
    </body>
</html>
'''

def test_get_links():
    links = UrlEMT.get_links(html_sample)
    assert isinstance(links, set)
    assert "files/trips_23_06_June.csv" in links
    assert "files/trips_22_12_December.csv" in links
    assert not any("pdf" in link for link in links)

def test_invalid_month_year():
    url_emt = UrlEMT()
    with pytest.raises(ValueError):
        url_emt.get_url(0, 21)  # Mes inválido
    with pytest.raises(ValueError):
        url_emt.get_url(5, 20)  # Año inválido

# Este test depende de conexión a internet y de que existan datos de ejemplo.
def test_valid_url():
    url_emt = UrlEMT()
    url = url_emt.get_url(6, 23)  # Junio 2023 debe existir
    assert "trips_23_06" in url


def test_get_csv():
    url_emt = UrlEMT()
    csv_file = url_emt.get_csv(6, 23)  # Junio 2023
    header_line = csv_file.readline()
    assert "idBike" in header_line or ";" in header_line