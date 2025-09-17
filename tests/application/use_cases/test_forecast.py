from pytest_mock import MockerFixture

from rebelist.momentum.application.use_cases import GetStockForecastUseCase
from rebelist.momentum.domain import Forecast, Stock


class TestGetStockForecastUseCase:
    """Tests for GetStockForecastUseCase ensuring it calls provider and simulator correctly."""

    def test_use_case_calls_provider_and_simulator(self, mocker: MockerFixture) -> None:
        """Test that the use case correctly calls provider and simulator and returns a Forecast."""
        mock_provider = mocker.MagicMock()
        mock_simulator = mocker.MagicMock()
        use_case = GetStockForecastUseCase(mock_provider, mock_simulator)

        stock = Stock(name='Test Stock', ticker='TST', currency='USD', history={1: 100.0})
        forecast = Forecast(stock, upper=[(1, 101.0)], median=[(1, 100.0)], lower=[(1, 99.0)])

        mock_provider.get_stock.return_value = stock
        mock_simulator.simulate.return_value = forecast

        result = use_case('TST', simulation_count=10, forecast_length=5)

        mock_provider.get_stock.assert_called_once_with('TST')
        mock_simulator.simulate.assert_called_once_with(stock, 10, 5)
        assert result == forecast
