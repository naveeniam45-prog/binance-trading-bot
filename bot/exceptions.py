"""Custom exceptions for the trading bot."""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""


class ValidationError(TradingBotError):
    """Raised when input validation fails."""


class APIError(TradingBotError):
    """Raised when a Binance API call fails."""

    def __init__(self, message: str, status_code: int | None = None, error_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class NetworkError(TradingBotError):
    """Raised when a network connectivity issue occurs."""


class AuthenticationError(TradingBotError):
    """Raised when API credentials are missing or invalid."""


class OrderError(TradingBotError):
    """Raised when order placement logic fails."""
