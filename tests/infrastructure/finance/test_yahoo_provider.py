from __future__ import annotations

from typing import Callable, Optional

import pytest
from pandas import DataFrame, Timestamp
from pytest_mock import MockerFixture
from yfinance import Ticker

from rebelist.momentum.domain import ProviderError, Stock
from rebelist.momentum.infrastructure.finance import YahooProvider


class TestYahooProvider:
    """Tests for YahooProvider with extended coverage and modern type hints."""

    def setup_method(self) -> None:
        """Reset provider for each test."""
        self.provider = YahooProvider()

    @staticmethod
    def mock_ticker(
        mocker: MockerFixture,
        info: dict[str, str | float | None] | None = None,
        history: Optional[DataFrame] = None,
        side_effect: Exception | Callable[..., Ticker] | None = None,
    ) -> None:
        """Ticker mock."""
        mock_ticker = mocker.MagicMock(spec=Ticker)
        if info is not None:
            mock_ticker.info = info
        if history is not None:
            mock_ticker.history.return_value = history
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.Ticker',
            return_value=mock_ticker,
            autospec=True,
            side_effect=side_effect,
        )

    def test_get_stock_returns_stock(self, mocker: MockerFixture) -> None:
        """Normal case returns Stock."""
        mock_history = DataFrame({'Close': [100.0, 101.0]}, index=[Timestamp('2025-09-15'), Timestamp('2025-09-16')])
        self.mock_ticker(
            mocker,
            info={'regularMarketPrice': 101.0, 'longName': 'Test Stock', 'currency': 'USD'},
            history=mock_history,
        )

        stock = self.provider.get_stock('TST')
        assert isinstance(stock, Stock)
        assert stock.name == 'Test Stock'
        assert stock.ticker == 'TST'
        assert stock.currency == 'USD'
        expected_history = {
            int(Timestamp('2025-09-15').timestamp() * 1000): 100.0,
            int(Timestamp('2025-09-16').timestamp() * 1000): 101.0,
        }
        assert stock.history == expected_history

    def test_empty_history_raises(self, mocker: MockerFixture) -> None:
        """Raises ProviderError when history is empty."""
        self.mock_ticker(
            mocker, info={'regularMarketPrice': 100.0, 'longName': 'Test', 'currency': 'USD'}, history=DataFrame()
        )

        with pytest.raises(ProviderError):
            self.provider.get_stock('EMPTY')

    def test_non_datetime_index_converted(self, mocker: MockerFixture) -> None:
        """Converts non-DatetimeIndex to datetime."""
        history = DataFrame({'Close': [100.0]}, index=['2025-09-15'])
        self.mock_ticker(
            mocker, info={'regularMarketPrice': 100.0, 'longName': 'Test', 'currency': 'USD'}, history=history
        )

        stock = self.provider.get_stock('NONDATE')
        ts = int(Timestamp('2025-09-15').timestamp() * 1000)
        assert ts in stock.history

    def test_all_nan_close_raises(self, mocker: MockerFixture) -> None:
        """Raises ProviderError when all Close values are NaN."""
        history = DataFrame(
            {'Close': [float('nan'), float('nan')]}, index=[Timestamp('2025-09-15'), Timestamp('2025-09-16')]
        )
        self.mock_ticker(
            mocker, info={'regularMarketPrice': 100.0, 'longName': 'Test', 'currency': 'USD'}, history=history
        )

        with pytest.raises(ProviderError):
            self.provider.get_stock('NAN')

    def test_partial_nan_history(self, mocker: MockerFixture) -> None:
        """Drops NaN rows but keeps valid rows."""
        history = DataFrame({'Close': [None, 101.0]}, index=[Timestamp('2025-09-15'), Timestamp('2025-09-16')])
        self.mock_ticker(
            mocker, info={'regularMarketPrice': 101.0, 'longName': 'Partial', 'currency': 'USD'}, history=history
        )

        stock = self.provider.get_stock('PARTIAL')
        ts = int(Timestamp('2025-09-16').timestamp() * 1000)
        assert stock.history.items() == {ts: 101.0}.items()
