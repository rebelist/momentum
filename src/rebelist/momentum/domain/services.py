from abc import ABC, abstractmethod

from rebelist.momentum.domain.models import Forecast, Stock


class ProviderError(Exception):
    """Raised when a FinanceProvider fails to fetch or process stock data."""

    ...


class FinanceProvider(ABC):
    """Abstract base class for financial data providers."""

    @abstractmethod
    def get_stock(self, symbol: str) -> Stock:
        """Get stock with price history."""
        ...


class FinanceSimulator(ABC):
    """Simulator for stock price forecasting."""

    @abstractmethod
    def simulate(self, stock: Stock, simulation_count: int, forecast_length: int) -> Forecast:
        """Perform multiple Monte Carlo simulations and calculates median and percentile bands."""
        ...
