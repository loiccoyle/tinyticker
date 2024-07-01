import pandas as pd
import pytest

from tinyticker.tickers._base import TickerResponse

from .utils import DATA_DIR


@pytest.fixture(scope="session")
def historical():
    return pd.read_pickle(DATA_DIR / "stock_historical.pkl")


@pytest.fixture(scope="session")
def ticker_response(historical):
    return TickerResponse(historical, historical.iloc[-1]["Close"])
