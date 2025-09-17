from rebelist.momentum.application.use_cases import GetStockForecastUseCase
from rebelist.momentum.config import Container


class TestContainer:
    """Sanity tests for the DI Container to ensure proper wiring of services."""

    def test_get_stock_forecast_use_case_is_singleton(self) -> None:
        """Test that the container provides a GetStockForecastUseCase instance."""
        container = Container()
        use_case = container.get_stock_forecast_use_case()

        assert isinstance(use_case, GetStockForecastUseCase)

        use_case2 = container.get_stock_forecast_use_case()
        assert use_case is use_case2
