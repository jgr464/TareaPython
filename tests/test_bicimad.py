import pandas as pd
import pytest

from bicimad.bicimad import BiciMad


def test_constructor_invalid_month_year():
    with pytest.raises(ValueError):
        BiciMad(0, 22)
    with pytest.raises(ValueError):
        BiciMad(13, 22)
    with pytest.raises(ValueError):
        BiciMad(5, 20)
    with pytest.raises(ValueError):
        BiciMad(5, 24)


def test_get_data_structure():
    bici = BiciMad(7, 21)  # Julio 2021 (usa un mes con datos seguros)
    df = bici.data

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "unlock_date"
    assert df.shape[1] == 14
    expected_cols = [
        'idBike', 'fleet', 'trip_minutes', 'geolocation_unlock', 'address_unlock',
        'locktype', 'unlocktype', 'geolocation_lock', 'address_lock', 'lock_date',
        'station_unlock', 'unlock_station_name', 'station_lock', 'lock_station_name'
    ]
    assert set(df.columns) == set(expected_cols)


def test_clean_method():
    bici = BiciMad(7, 21)
    bici.clean()
    df = bici.data

    assert df.index.name == 'fecha'
    assert df.index.dtype == object or df.index.dtype.name.startswith("date")  # .date elimina time
    assert df.isna().all(axis=1).sum() == 0
    for col in ['fleet', 'idBike', 'station_lock', 'station_unlock']:
        assert df[col].dtype == object  # str in pandas is 'object'


def test_resume_output():
    bici = BiciMad(7, 21)
    bici.clean()
    resumen = bici.resume()

    assert isinstance(resumen, pd.Series)
    assert resumen.index.tolist() == [
        'year', 'month', 'total_uses', 'total_time', 'most_popular_station', 'uses_from_most_popular'
    ]
    assert resumen['year'] == 21
    assert resumen['month'] == 7
    assert resumen['total_uses'] > 0
    assert resumen['total_time'] > 0
    assert isinstance(resumen['most_popular_station'], set)
    assert resumen['uses_from_most_popular'] > 0

@pytest.fixture
def sample_bicimad():
    data = {
        "trip_minutes": [10, 20, 30, 15, 45],
        "address_unlock": [
            "Estación A", "Estación B", "Estación A", "Estación C", "Estación A"
        ],
        "station_unlock": ["001", "002", "001", "003", "001"],
        "lock_date": pd.to_datetime([
            "2022-05-01 ", "2022-05-01 ",
            "2022-05-02 ", "2022-05-02 ",
            "2022-05-02 "
        ])
    }
    df = pd.DataFrame(data)
    df.index = pd.to_datetime([
        "2022-05-01 ", "2022-05-01 ",
        "2022-05-02 ", "2022-05-02 ",
        "2022-05-02 "
    ])
    # Creamos un objeto BiciMad con datos falsos
    bici = BiciMad(5, 22)
    bici._data = df  # sobrescribimos para no depender de EMT
    return bici


def test_day_time(sample_bicimad):
    result = sample_bicimad.day_time()

    expected = pd.Series(
        data=[0.5, 1.5],
        index=pd.to_datetime(["2022-05-01", "2022-05-02"]),
        name="trip_minutes"
    )

    # Verificamos que ambos índices y valores son iguales
    pd.testing.assert_series_equal(result, expected)


def test_weekday_time(sample_bicimad):
    result = sample_bicimad.weekday_time()
    assert isinstance(result, pd.Series)
    assert "D" in result.index or "L" in result.index # días de semana abreviados


def test_total_usage_day(sample_bicimad):
    result = sample_bicimad.total_usage_day()
    assert result.loc[pd.Timestamp("2022-05-01")] == 2


def test_total_usage_by_station_day(sample_bicimad):
    result = sample_bicimad.total_usage_by_station_day()
    assert ("2022-05-01", "001") in result.index  # multiíndice
    assert result.loc[("2022-05-01", "001")] == 1


def test_most_popular_stations(sample_bicimad):
    result = sample_bicimad.most_popular_stations()
    assert isinstance(result, set)
    assert "Estación A" in result  # es la más usada


def test_usage_from_most_popular_station(sample_bicimad):
    result = sample_bicimad.usage_from_most_popular_station()
    assert isinstance(result, pd.Series)
    assert result.iloc[0] == 3  # Estación A tiene 3 usos
