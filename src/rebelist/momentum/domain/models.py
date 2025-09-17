from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stock:
    """Represents a financial stock with its identifying information and future price forecast."""

    name: str
    ticker: str
    history: dict[int, float]


@dataclass(frozen=True, slots=True)
class Forecast:
    """Represents a financial price forecast."""

    stock: Stock
    upper: list[tuple[int, float]]
    median: list[tuple[int, float]]
    lower: list[tuple[int, float]]
