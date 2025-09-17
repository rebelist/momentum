from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton

from rebelist.momentum.application.use_cases import GetStockForecastUseCase
from rebelist.momentum.infrastructure.finance import YahooProvider
from rebelist.momentum.infrastructure.forecast import MonteCarloSimulator


class Container(DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = WiringConfiguration(
        auto_wire=True,
        packages=['rebelist.momentum.presentation'],
    )

    ### Private Services ###

    __finance_provider = Singleton(YahooProvider)

    __finance_simulator = Singleton(MonteCarloSimulator)

    ### Public Services ###
    get_stock_forecast_use_case = Singleton(GetStockForecastUseCase, __finance_provider, __finance_simulator)
