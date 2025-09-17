from nicegui.elements.column import Column
from nicegui.elements.input import Input
from nicegui.elements.label import Label
from nicegui.elements.number import Number
from nicegui_highcharts.highchart import Highchart
from pytest_mock import MockerFixture

from rebelist.momentum.application.use_cases.forecast import GetStockForecastUseCase
from rebelist.momentum.domain import Forecast, Stock
from rebelist.momentum.presentation.models import Dashboard


class TestDashboard:
    """Test dashboard."""

    def test_validate_with_empty_ticker(self, mocker: MockerFixture) -> None:
        """Test validate returns False and notifies user when ticker is empty."""
        mock_input = mocker.MagicMock(spec=Input)
        mock_input.value = '   '
        mock_notify = mocker.patch('rebelist.momentum.presentation.models.ui.notify', autospec=True)

        dashboard = Dashboard(
            ticker=mock_input,
            title=mocker.MagicMock(spec=Label),
            simulation_count=mocker.MagicMock(spec=Number),
            forecast_length=mocker.MagicMock(spec=Number),
            chart=mocker.MagicMock(spec=Column),
            get_stock_forecast=mocker.MagicMock(spec=GetStockForecastUseCase),
        )

        result = dashboard.validate()

        assert result is False
        mock_notify.assert_called_once_with('Please enter a ticker symbol.', color='red')

    def test_validate_with_valid_ticker(self, mocker: MockerFixture) -> None:
        """Test validate returns True when ticker is not empty."""
        mock_input = mocker.MagicMock()
        mock_input.value = 'aapl'

        dashboard = Dashboard(
            ticker=mock_input,
            title=mocker.MagicMock(spec=Label),
            simulation_count=mocker.MagicMock(spec=Number),
            forecast_length=mocker.MagicMock(spec=Number),
            chart=mocker.MagicMock(spec=Column),
            get_stock_forecast=mocker.MagicMock(spec=GetStockForecastUseCase),
        )

        result = dashboard.validate()

        assert result is True
        assert mock_input.value == 'aapl'  # value unchanged here

    def test_update_invalid_ticker_does_not_call_forecast(self, mocker: MockerFixture) -> None:
        """Test update does nothing when validate fails."""
        mock_input = mocker.MagicMock(spec=Input)
        mock_input.value = ' '
        mock_chart = mocker.MagicMock(spec=Column)
        mock_get_stock_forecast = mocker.MagicMock(spec=GetStockForecastUseCase)
        mock_notify = mocker.patch('rebelist.momentum.presentation.models.ui.notify', autospec=True)

        dashboard = Dashboard(
            ticker=mock_input,
            title=mocker.MagicMock(spec=Label),
            simulation_count=mocker.MagicMock(spec=Number),
            forecast_length=mocker.MagicMock(spec=Number),
            chart=mock_chart,
            get_stock_forecast=mock_get_stock_forecast,
        )

        dashboard.update()

        mock_chart.clear.assert_not_called()
        mock_get_stock_forecast.assert_not_called()
        mock_notify.assert_called_once()

    def test_update_valid_flow(self, mocker: MockerFixture) -> None:
        """Test update clears chart, uppercases ticker, calls forecast, updates title, and renders chart."""
        mock_input = mocker.MagicMock(spec=Input)
        mock_input.value = 'MSFT'
        mock_title = mocker.MagicMock(spec=Label)
        mock_sim_count = mocker.MagicMock(spec=Number)
        mock_sim_count.value = 100
        mock_forecast_length = mocker.MagicMock(spec=Number)
        mock_forecast_length.value = 30
        mock_chart = mocker.MagicMock(spec=Column)

        stock = Stock(name='Microsoft', ticker='MSFT', history={})
        forecast = Forecast(
            stock=stock,
            upper=[(1, 200.0)],
            median=[(1, 150.0)],
            lower=[(1, 100.0)],
        )
        mock_get_stock_forecast = mocker.MagicMock(return_value=forecast)

        mock_highchart = mocker.patch('rebelist.momentum.presentation.models.ui.highchart', autospec=True)
        mock_highchart.return_value = mocker.MagicMock(spec=Highchart)

        dashboard = Dashboard(
            ticker=mock_input,
            title=mock_title,
            simulation_count=mock_sim_count,
            forecast_length=mock_forecast_length,
            chart=mock_chart,
            get_stock_forecast=mock_get_stock_forecast,
        )

        dashboard.update()

        mock_chart.clear.assert_called_once()
        assert mock_input.value == 'MSFT'
        mock_get_stock_forecast.assert_called_once_with('MSFT', 100, 30)
        assert mock_title.text == 'Microsoft'
        mock_highchart.assert_called_once()
        mock_highchart.return_value.classes.assert_called_once_with('w-full h-[700px]')
