from nicegui.elements.button import Button
from nicegui.elements.column import Column
from nicegui.elements.input import Input
from nicegui.elements.label import Label
from nicegui.elements.number import Number
from pytest_mock import MockerFixture

from rebelist.momentum.application.use_cases.forecast import GetStockForecastUseCase
from rebelist.momentum.config import Container
from rebelist.momentum.presentation.dashboard import index


class TestDashboardIndexPage:
    """Dashboard index page test."""

    def test_index_creates_ui_elements_and_dashboard(self, mocker: MockerFixture) -> None:
        """Test that index sets up UI elements and Dashboard correctly."""
        mock_ui = mocker.patch('rebelist.momentum.presentation.dashboard.ui', autospec=True)
        mock_container = mocker.MagicMock(spec=Container)
        mock_use_case = mocker.MagicMock(spec=GetStockForecastUseCase)
        mock_container.get_stock_forecast_use_case.return_value = mock_use_case
        mocker.patch('rebelist.momentum.presentation.dashboard.Container', return_value=mock_container, autospec=True)

        index()

        mock_ui.header.assert_called_once()
        mock_ui.row.assert_called_once()
        mock_ui.input.assert_called_once_with('Ticker Symbol', placeholder='e.g., VOO')
        mock_ui.number.assert_any_call(label='Simulations', min=10, max=5000, value=100, step=1)
        mock_ui.number.assert_any_call(label='Forecast Days', min=30, max=600, value=200, step=1)
        mock_ui.label.assert_any_call()
        mock_ui.button.assert_called_once_with('Run Simulation')
        mock_ui.column.assert_called_once()

        mock_container.get_stock_forecast_use_case.assert_called_once()

    def test_index_ui_event_connections(self, mocker: MockerFixture) -> None:
        """Test that UI events are connected to Dashboard.update."""
        mock_ui = mocker.patch('rebelist.momentum.presentation.dashboard.ui', autospec=True)
        mock_container = mocker.MagicMock()
        mock_use_case = mocker.MagicMock()
        mock_container.get_stock_forecast_use_case.return_value = mock_use_case
        mocker.patch('rebelist.momentum.presentation.dashboard.Container', return_value=mock_container)

        mock_input = mocker.MagicMock(spec=Input)
        mock_button = mocker.MagicMock(spec=Button)
        mock_ui.input.return_value = mock_input
        mock_ui.button.return_value = mock_button
        mock_ui.number.return_value = mocker.MagicMock(spec=Number)
        mock_ui.label.return_value = mocker.MagicMock(spec=Label)
        mock_ui.column.return_value = mocker.MagicMock(spec=Column)

        index()

        mock_input.on.assert_called_once()
        mock_button.on.assert_called_once()
