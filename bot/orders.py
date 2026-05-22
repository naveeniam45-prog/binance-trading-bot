"""Order placement logic — business layer between CLI and API client."""

import logging
from dataclasses import dataclass

from bot.client import BinanceFuturesClient
from bot.exceptions import APIError, NetworkError, OrderError
from bot.validators import OrderRequest, OrderType

logger = logging.getLogger("trading_bot")


def _resolve_avg_price(raw: dict) -> str:
    """Return avgPrice when filled, otherwise fall back to the limit price field."""
    avg = raw.get("avgPrice", "0")
    if avg and avg != "0":
        return avg
    return raw.get("price", "0")


@dataclass
class OrderResponse:
    """Structured representation of a Binance Futures order response."""

    order_id: int
    symbol: str
    side: str
    order_type: str
    status: str
    orig_qty: str
    executed_qty: str
    avg_price: str
    raw: dict


def place_order(request: OrderRequest, client: BinanceFuturesClient) -> OrderResponse:
    """Place a MARKET or LIMIT order and return a structured response.

    Raises APIError, NetworkError, or OrderError on failure.
    """
    try:
        if request.order_type == OrderType.MARKET:
            raw = client.create_market_order(
                symbol=request.symbol,
                side=request.side.value,
                quantity=float(request.quantity),
            )
        else:
            raw = client.create_limit_order(
                symbol=request.symbol,
                side=request.side.value,
                quantity=float(request.quantity),
                price=float(request.price),  # type: ignore[arg-type]
            )

        response = OrderResponse(
            order_id=int(raw.get("orderId", 0)),
            symbol=raw.get("symbol", request.symbol),
            side=raw.get("side", request.side.value),
            order_type=raw.get("type", request.order_type.value),
            status=raw.get("status", "UNKNOWN"),
            orig_qty=raw.get("origQty", str(request.quantity)),
            executed_qty=raw.get("executedQty", "0"),
            avg_price=_resolve_avg_price(raw),
            raw=raw,
        )
        logger.info(
            "Order placed | id=%s symbol=%s side=%s type=%s status=%s",
            response.order_id,
            response.symbol,
            response.side,
            response.order_type,
            response.status,
        )
        return response

    except (APIError, NetworkError):
        raise
    except Exception as exc:
        logger.error("Unexpected error in place_order: %s", exc)
        raise OrderError(f"Failed to place order: {exc}") from exc
