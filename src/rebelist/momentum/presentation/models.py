from dataclasses import dataclass

from nicegui import ui
from nicegui.elements.column import Column
from nicegui.elements.input import Input
from nicegui.elements.label import Label
from nicegui.elements.number import Number

from rebelist.momentum.application.use_cases import GetStockForecastUseCase
from rebelist.momentum.domain import Forecast, ProviderError


@dataclass(frozen=True, slots=True)
class Dashboard:
    """UI Dashboard elements."""

    ticker: Input
    title: Label
    simulation_count: Number
    forecast_length: Number
    chart: Column
    get_stock_forecast: GetStockForecastUseCase

    def update(self) -> None:
        """Updates the chart based on UI settings."""
        if not self.validate():
            return

        self.chart.clear()

        try:
            forecast: Forecast = self.get_stock_forecast(
                str(self.ticker.value).upper(), int(self.simulation_count.value), int(self.forecast_length.value)
            )
        except ProviderError as error:
            ui.notify(f'ERROR: {error}', color='red')
            return

        self.title.text = forecast.stock.name

        with self.chart:
            ui.highchart(
                {
                    'chart': {'type': 'area', 'height': 700},
                    'title': False,
                    'credits': {'enabled': False},
                    'xAxis': {
                        'type': 'datetime',
                        'tickInterval': 30 * 24 * 3600 * 1000,  # ~1 month
                        'dateTimeLabelFormats': {
                            'month': '%b %Y',
                            'year': '%b %Y',
                        },
                    },
                    'yAxis': {'title': {'text': 'Price'}},
                    'plotOptions': {
                        'area': {'lineWidth': 2, 'fillOpacity': 0.3},
                        'line': {'lineWidth': 2},
                    },
                    'series': [
                        {
                            'name': 'Upper',
                            'data': forecast.upper,
                            'type': 'area',
                            'color': 'rgba(50,200,50,0.3)',
                            'showInLegend': True,
                        },
                        {
                            'name': 'Median',
                            'data': forecast.median,
                            'color': 'rgba(50,50,200,0.3)',
                        },
                        {
                            'name': 'Lower',
                            'data': forecast.lower,
                            'type': 'area',
                            'color': 'rgba(200,50,50,0.4)',
                            'showInLegend': True,
                        },
                    ],
                }
            ).classes('w-full h-[700px]')

    def validate(self) -> bool:
        """Validates the dashboard."""
        ticker: str = self.ticker.value.strip().upper()

        if not ticker:
            ui.notify('Please enter a ticker symbol.', color='red')
            return False

        return True
