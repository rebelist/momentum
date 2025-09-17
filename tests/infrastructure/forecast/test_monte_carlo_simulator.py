from datetime import datetime, timedelta

import pytest
from pytest_mock import MockerFixture

from rebelist.momentum.domain import Forecast, Stock
from rebelist.momentum.infrastructure.forecast import MonteCarloSimulator


class TestMonteCarloSimulator:
    """Test for Monte Carlo simulator."""

    def test_simulate_returns_forecast_with_correct_structure(self) -> None:
        """Test that simulate returns a Forecast with correct upper, median, and lower lists."""
        # Prepare a stock with some history
        now = datetime(2025, 9, 17, 10, 0, 0)
        timestamps: dict[int, float] = {int((now - timedelta(days=i)).timestamp() * 1000): 100 + i for i in range(10)}
        stock = Stock(name='TestStock', ticker='TST', currency='USD', history=timestamps)

        simulator = MonteCarloSimulator()
        forecast_length = 5
        simulation_count = 100

        forecast = simulator.simulate(stock, simulation_count, forecast_length)

        assert isinstance(forecast, Forecast)
        assert len(forecast.median) == forecast_length
        assert len(forecast.lower) == forecast_length
        assert len(forecast.upper) == forecast_length

        for lower, median, upper in zip(forecast.lower, forecast.median, forecast.upper, strict=True):
            assert isinstance(lower, tuple) and len(lower) == 2
            assert isinstance(median, tuple) and len(median) == 2
            assert isinstance(upper, tuple) and len(upper) == 2
            assert lower[1] <= median[1] <= upper[1]

    def test_simulate_raises_error_on_empty_history(self) -> None:
        """Test that simulate raises ValueError when stock.history is empty."""
        stock = Stock(name='EmptyStock', ticker='EMP', currency='USD', history={})
        simulator = MonteCarloSimulator()
        with pytest.raises(ValueError, match='The stock has no price history.'):
            simulator.simulate(stock, simulation_count=10, forecast_length=5)

    def test_simulate_with_constant_prices(self, mocker: MockerFixture) -> None:
        """Test simulate behavior when stock prices are constant with deterministic randomness."""
        now = datetime(2025, 9, 17, 10, 0, 0)
        timestamps = {int((now - timedelta(days=i)).timestamp() * 1000): 100.0 for i in range(10)}
        stock = Stock(name='ConstantStock', ticker='CONST', currency='USD', history=timestamps)

        mocker.patch('numpy.random.normal', return_value=0.0, autospec=True)

        simulator = MonteCarloSimulator()
        forecast = simulator.simulate(stock, simulation_count=50, forecast_length=3)

        last_price = 100.0
        for _, price in forecast.median:
            assert price == last_price
        for _, price in forecast.lower:
            assert price == last_price
        for _, price in forecast.upper:
            assert price == last_price
