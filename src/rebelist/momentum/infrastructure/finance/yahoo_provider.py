from typing import cast

import numpy
import yfinance as client
from pandas import Timestamp
from yfinance import Ticker

from rebelist.momentum.domain import FinanceProvider, ProviderError, Stock


class YahooProvider(FinanceProvider):
    """FinanceProvider implementation using Yahoo Finance as a data source."""

    def __init__(self):
        client.set_tz_cache_location('var/cache')

    def get_stock(self, symbol: str) -> Stock:
        """Fetch historical stock price data from Yahoo Finance."""
        try:
            ticker = Ticker(symbol)

            if not ticker.info or ticker.info.get('regularMarketPrice') is None:
                raise ValueError(f"Ticker '{symbol}' appears to be invalid or delisted.")
        except Exception as e:
            raise ProviderError(f"Failed to fetch price history for ticker '{symbol}'.") from e

        name = cast(str, ticker.info.get('longName'))
        history = {
            int(cast(Timestamp, date).timestamp() * 1000): float(cast(numpy.float64, row['Close']))
            for date, row in ticker.history(period='max', auto_adjust=True, actions=False).iterrows()
        }

        return Stock(name, symbol, history)
