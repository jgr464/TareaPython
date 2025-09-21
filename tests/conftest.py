# tests/conftest.py

import pytest
import truststore


@pytest.fixture(scope="session", autouse=True)
def activate_ssl_truststore():
    """Activa truststore para todo el entorno de tests antes de que se ejecuten."""
    truststore.inject_into_ssl()
