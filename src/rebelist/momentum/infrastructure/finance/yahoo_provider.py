from typing import Final, cast

import numpy
import yfinance as client
from pandas import DataFrame, DateOffset, DatetimeIndex, Timestamp, to_datetime
from yfinance import Ticker

from rebelist.momentum.domain import FinanceProvider, ProviderError, Stock


class YahooProvider(FinanceProvider):
    """FinanceProvider implementation using Yahoo Finance as a data source."""

    LOOPBACK_YEARS: Final[int] = 5

    def __init__(self):
        client.set_tz_cache_location('var/cache')

    def get_stock(self, symbol: str) -> Stock:
        """Fetch historical stock price data from Yahoo Finance with hygiene and lookback."""
        try:
            ticker = Ticker(symbol)

            if not ticker.info or ticker.info.get('regularMarketPrice') is None:
                raise ValueError(f"Ticker '{symbol}' appears to be invalid or delisted.")

            ticker_history: DataFrame = ticker.history(period='max', auto_adjust=True, actions=False)
        except Exception as e:
            raise ProviderError(f"Failed to fetch price history for ticker '{symbol}'.") from e

        if ticker_history.empty:
            raise ProviderError(f"No price history available for ticker '{symbol}'.")

        if not isinstance(ticker_history.index, DatetimeIndex):
            try:
                ticker_history.index = to_datetime(ticker_history.index)
            except Exception as e:
                raise ProviderError(f"Invalid date index for ticker '{symbol}'.") from e

        ticker_history = ticker_history.sort_index()
        ticker_history = ticker_history.dropna(subset=['Close'])

        cutoff = cast(Timestamp, ticker_history.index.max() - DateOffset(years=self.LOOPBACK_YEARS))
        ticker_history = ticker_history[ticker_history.index >= cutoff]

        if ticker_history.empty:
            raise ProviderError(
                f"Insufficient price history for ticker '{symbol}' in the last {self.LOOPBACK_YEARS} years."
            )

        name = cast(str, ticker.info.get('longName'))
        currency = cast(str, ticker.info.get('currency'))

        history = {
            int(cast(Timestamp, date).timestamp() * 1000): float(cast(numpy.float64, row['Close']))
            for date, row in ticker_history.iterrows()
        }

        return Stock(name, symbol, currency, dict(sorted(history.items())))
