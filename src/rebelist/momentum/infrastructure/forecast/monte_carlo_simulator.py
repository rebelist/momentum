from datetime import datetime
from typing import Final

import numpy as numpy
from pandas import Timedelta, bdate_range

from rebelist.momentum.domain import FinanceSimulator, Forecast, Stock


class MonteCarloSimulator(FinanceSimulator):
    """Monte Carlo simulator for stock price forecasting."""

    LOWER_PERCENTIL: Final[int] = 10
    UPPER_PERCENTIL: int = 90

    def simulate(self, stock: Stock, simulation_count: int, forecast_length: int) -> Forecast:
        """Perform multiple Monte Carlo simulations and calculate median and percentile bands."""
        history = stock.history
        if not history:
            raise ValueError('The stock has no price history.')

        last_timestamp, last_price = next(reversed(history.items()))
        last_price = float(last_price)
        start_date = datetime.fromtimestamp(last_timestamp / 1000)

        prices = numpy.array(list(history.values()), dtype=float)
        returns = numpy.log(prices[1:] / prices[:-1])

        # Business-day future timeline (skip weekends)
        future_dates = bdate_range(start=start_date + Timedelta(days=1), periods=forecast_length)
        future_timestamps = [int(date.timestamp() * 1000) for date in future_dates]

        average_daily_move: float = float(returns.mean())
        standard_deviation: float = float(returns.std(ddof=1))

        all_simulations: numpy.ndarray = numpy.zeros((simulation_count, forecast_length), dtype=float)

        for sim in range(simulation_count):
            price: float = last_price
            for day in range(forecast_length):
                shock: float = numpy.random.normal(average_daily_move, standard_deviation)
                price = price * numpy.exp(shock)
                all_simulations[sim, day] = price

        median_prices = numpy.median(all_simulations, axis=0)
        lower_prices = numpy.percentile(all_simulations, self.LOWER_PERCENTIL, axis=0)
        upper_prices = numpy.percentile(all_simulations, self.UPPER_PERCENTIL, axis=0)

        median = [(date, round(float(p), 2)) for date, p in zip(future_timestamps, median_prices, strict=True)]
        lower = [(date, round(float(p), 2)) for date, p in zip(future_timestamps, lower_prices, strict=True)]
        upper = [(date, round(float(p), 2)) for date, p in zip(future_timestamps, upper_prices, strict=True)]

        return Forecast(stock, upper, median, lower)
