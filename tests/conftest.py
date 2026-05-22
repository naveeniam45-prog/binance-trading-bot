"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def market_request():
    from bot.validators import OrderRequest
    return OrderRequest(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="0.001")


@pytest.fixture
def limit_request():
    from bot.validators import OrderRequest
    return OrderRequest(symbol="ETHUSDT", side="SELL", order_type="LIMIT", quantity="1.0", price="3000")


MARKET_RAW_RESPONSE = {
    "orderId": 3947582,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "status": "FILLED",
    "origQty": "0.001",
    "executedQty": "0.001",
    "avgPrice": "64250.55",
    "price": "0",
    "timeInForce": "GTC",
    "cumQuote": "64.25055",
    "updateTime": 1705330827000,
}

LIMIT_RAW_RESPONSE = {
    "orderId": 3947589,
    "symbol": "ETHUSDT",
    "side": "SELL",
    "type": "LIMIT",
    "status": "NEW",
    "origQty": "1.0",
    "executedQty": "0.000",
    "avgPrice": "0",
    "price": "3000",
    "timeInForce": "GTC",
    "cumQuote": "0",
    "updateTime": 1705330853000,
}
