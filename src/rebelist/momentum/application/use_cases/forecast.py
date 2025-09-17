from rebelist.momentum.domain import FinanceProvider, FinanceSimulator, Forecast


class GetStockForecastUseCase:
    """Application use case for generating a stock price forecast."""

    def __init__(self, provider: FinanceProvider, simulator: FinanceSimulator) -> None:
        self.__provider = provider
        self.__simulator = simulator

    def __call__(self, symbol: str, simulation_count: int, forecast_length: int) -> Forecast:
        """Execute the use case to generate a forecast for a given stock symbol."""
        stock = self.__provider.get_stock(symbol)
        forecast = self.__simulator.simulate(stock, simulation_count, forecast_length)

        return forecast
