import pytest
from pandas import DataFrame, Timestamp
from pytest_mock import MockerFixture
from yfinance import Ticker

from rebelist.momentum.domain import ProviderError, Stock
from rebelist.momentum.infrastructure.finance import YahooProvider


class TestYahooProvider:
    """Tests for YahooProvider, ensuring it correctly fetches stock data and handles errors."""

    def test_get_stock_returns_stock(self, mocker: MockerFixture) -> None:
        """Test that get_stock returns a Stock object with proper data."""
        mock_history = DataFrame(
            {'Close': [100.0, 101.0]}, index=[Timestamp('2025-09-15 00:00'), Timestamp('2025-09-16')]
        )
        mock_ticker = mocker.MagicMock(spec=Ticker)
        mock_ticker.info = {'regularMarketPrice': 101.0, 'longName': 'Test Stock', 'currency': 'USD'}
        mock_ticker.history.return_value = mock_history

        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.Ticker', return_value=mock_ticker, autospec=True
        )
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.client.set_tz_cache_location', autospec=True
        )

        provider = YahooProvider()
        stock = provider.get_stock('TST')

        assert isinstance(stock, Stock)
        assert stock.name == 'Test Stock'
        assert stock.ticker == 'TST'
        assert stock.currency == 'USD'
        expected_history: dict[int, float] = {
            int(Timestamp('2025-09-15').timestamp() * 1000): 100.0,
            int(Timestamp('2025-09-16').timestamp() * 1000): 101.0,
        }
        assert stock.history == expected_history

    def test_get_stock_invalid_ticker_raises(self, mocker: MockerFixture) -> None:
        """Test that get_stock raises ProviderError when ticker is invalid."""
        mock_ticker = mocker.MagicMock()
        mock_ticker.info = {'regularMarketPrice': None}
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.Ticker', return_value=mock_ticker, autospec=True
        )
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.client.set_tz_cache_location', autospec=True
        )

        provider = YahooProvider()
        with pytest.raises(ProviderError):
            provider.get_stock('INVALID')

    def test_get_stock_exception_raises(self, mocker: MockerFixture) -> None:
        """Test that get_stock raises ProviderError on exception."""
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.Ticker', side_effect=Exception('Network error')
        )
        mocker.patch(
            'rebelist.momentum.infrastructure.finance.yahoo_provider.client.set_tz_cache_location', autospec=True
        )

        provider = YahooProvider()
        with pytest.raises(ProviderError):
            provider.get_stock('ANY')
