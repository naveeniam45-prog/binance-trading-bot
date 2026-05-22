"""Binance Futures client wrapper — API layer only, no business logic."""

import logging

import requests
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from bot.config import settings
from bot.exceptions import APIError, AuthenticationError, NetworkError

logger = logging.getLogger("trading_bot")


class BinanceFuturesClient:
    """Thin wrapper around python-binance targeting the Futures Testnet."""

    def __init__(self) -> None:
        self._client: Client = self._build_client()

    def _build_client(self) -> Client:
        if not settings.binance_api_key or not settings.binance_api_secret:
            raise AuthenticationError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file"
            )
        try:
            client = Client(
                api_key=settings.binance_api_key,
                api_secret=settings.binance_api_secret,
                testnet=settings.binance_testnet,
            )
            logger.info("Binance Futures client initialised (testnet=%s)", settings.binance_testnet)
            return client
        except Exception as exc:
            logger.error("Client init failed: %s", exc)
            raise AuthenticationError(f"Failed to initialise Binance client: {exc}") from exc

    # ------------------------------------------------------------------
    # Public order helpers
    # ------------------------------------------------------------------

    def create_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Place a MARKET order on Binance Futures."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": Client.ORDER_TYPE_MARKET,
            "quantity": quantity,
        }
        logger.info(
            "REQUEST | MARKET order | symbol=%s side=%s quantity=%s",
            symbol, side, quantity,
        )
        return self._execute(params)

    def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = Client.TIME_IN_FORCE_GTC,
    ) -> dict:
        """Place a LIMIT order on Binance Futures."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": Client.ORDER_TYPE_LIMIT,
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
        }
        logger.info(
            "REQUEST | LIMIT order | symbol=%s side=%s quantity=%s price=%s",
            symbol, side, quantity, price,
        )
        return self._execute(params)

    def get_account_balance(self) -> list[dict]:
        """Return futures account balances with a non-zero balance."""
        try:
            balances: list[dict] = self._client.futures_account_balance()
            non_zero = [b for b in balances if float(b.get("balance", 0)) != 0]
            logger.info("Fetched account balance (%d assets)", len(non_zero))
            return non_zero
        except BinanceAPIException as exc:
            logger.error("Balance fetch failed | code=%s msg=%s", exc.code, exc.message)
            raise APIError(exc.message, status_code=exc.status_code, error_code=exc.code) from exc

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _execute(self, params: dict) -> dict:
        try:
            response: dict = self._client.futures_create_order(**params)
            logger.info("RESPONSE | %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error("API error | code=%s msg=%s", exc.code, exc.message)
            raise APIError(exc.message, status_code=exc.status_code, error_code=exc.code) from exc
        except BinanceOrderException as exc:
            logger.error("Order exception | code=%s msg=%s", exc.code, exc.message)
            raise APIError(exc.message, error_code=exc.code) from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise NetworkError(f"Connection failed — check your internet: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timeout: %s", exc)
            raise NetworkError(f"Request timed out: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected error: %s", exc)
            raise APIError(f"Unexpected error: {exc}") from exc
