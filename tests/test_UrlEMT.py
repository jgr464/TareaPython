import pytest

from bicimad.UrlEMT import UrlEMT


# HTML de prueba simulado
def test_get_links():
    html_sample = '''
    <html>
        <body>
            <a href="bicimad_2023/trips_23_06_June-csv.zip">Junio</a>
            <a href="bicimad_2022/trips_22_12_December-csv.zip">Diciembre</a>
            <a href="bicimad_2022/otherfile.pdf">Otro archivo</a>
        </body>
    </html>
    '''
    links = UrlEMT.get_links(html_sample)

    assert isinstance(links, set)
    assert "bicimad_2023/trips_23_06_June-csv.zip" in links
    assert "bicimad_2022/trips_22_12_December-csv.zip" in links
    assert all("pdf" not in link for link in links)


def test_invalid_month_year():
    url_emt = UrlEMT()

    with pytest.raises(ValueError):
        url_emt.get_url(0, 22)

    with pytest.raises(ValueError):
        url_emt.get_url(13, 22)

    with pytest.raises(ValueError):
        url_emt.get_url(5, 20)

    with pytest.raises(ValueError):
        url_emt.get_url(5, 24)


def test_get_url_real():
    url_emt = UrlEMT()
    url = url_emt.get_url(1, 23)  # Enero 2023 por ejemplo
    assert "trips_23_01_" in url
    assert url.startswith("https://")


def test_get_csv_real():
    url_emt = UrlEMT()
    csv_file = url_emt.get_csv(1, 23)  # Enero 2023
    content = csv_file.read(1024)
    assert isinstance(content, str)
    assert len(content) > 0
    assert "start_date" in content or "id" in content.lower()
