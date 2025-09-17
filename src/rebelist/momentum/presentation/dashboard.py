from nicegui import ui

from rebelist.momentum.config import Container
from rebelist.momentum.presentation.models import Dashboard


@ui.page('/')
def index() -> None:
    """Define the dashboard page layout."""
    container = Container()
    use_case = container.get_stock_forecast_use_case()

    with ui.header().classes('items-center bg-blue-100'):
        ui.label('Momentum').classes('text-xl font-bold text-primary')
        ui.label('|').classes('text-xl text-primary')
        ui.label('Future Stock Price Simulation').classes('text-xl text-primary')
        ui.space()

    with ui.row().classes('items-center'):
        ticker = ui.input('Ticker Symbol', placeholder='e.g., VOO')
        simulation_count = ui.number(label='Simulations', min=10, max=5000, value=100, step=1).classes('ml-4 w-[120px]')
        forecast_length = ui.number(label='Forecast Days', min=30, max=600, value=200, step=1).classes('ml-4 w-[120px]')
        title = ui.label().classes('ml-[50px] text-xl text-bold text-gray-400')

    submit = ui.button('Run Simulation')
    chart = ui.column().classes('w-full h-[700px]')

    dashboard = Dashboard(ticker, title, simulation_count, forecast_length, chart, use_case)
    ticker.on('keydown.enter', dashboard.update)
    submit.on('click', dashboard.update)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(show=False, reload=False)
