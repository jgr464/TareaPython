import pytest
import pandas as pd
from bicimad.bicimad  import BiciMad


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