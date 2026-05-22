"""Tests for bot.validators — no network or API calls."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from bot.validators import OrderRequest, OrderSide, OrderType


# ---------------------------------------------------------------------------
# Valid inputs
# ---------------------------------------------------------------------------


def test_valid_market_buy():
    req = OrderRequest(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="0.001")
    assert req.symbol == "BTCUSDT"
    assert req.side == OrderSide.BUY
    assert req.order_type == OrderType.MARKET
    assert req.quantity == Decimal("0.001")
    assert req.price is None


def test_valid_limit_sell():
    req = OrderRequest(
        symbol="ETHUSDT", side="SELL", order_type="LIMIT", quantity="1.5", price="3000"
    )
    assert req.side == OrderSide.SELL
    assert req.order_type == OrderType.LIMIT
    assert req.price == Decimal("3000")


def test_symbol_normalised_to_uppercase():
    req = OrderRequest(symbol="btcusdt", side="BUY", order_type="MARKET", quantity="0.001")
    assert req.symbol == "BTCUSDT"


def test_side_normalised_to_uppercase():
    req = OrderRequest(symbol="BTCUSDT", side="buy", order_type="MARKET", quantity="0.001")
    assert req.side == OrderSide.BUY


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------


def test_limit_without_price_raises():
    with pytest.raises(ValidationError, match="Price is required for LIMIT"):
        OrderRequest(symbol="BTCUSDT", side="BUY", order_type="LIMIT", quantity="0.001")


def test_invalid_side_raises():
    with pytest.raises(ValidationError):
        OrderRequest(symbol="BTCUSDT", side="HOLD", order_type="MARKET", quantity="0.001")


def test_invalid_order_type_raises():
    with pytest.raises(ValidationError):
        OrderRequest(symbol="BTCUSDT", side="BUY", order_type="STOP", quantity="0.001")


def test_negative_quantity_raises():
    with pytest.raises(ValidationError, match="greater than 0"):
        OrderRequest(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="-0.5")


def test_zero_quantity_raises():
    with pytest.raises(ValidationError, match="greater than 0"):
        OrderRequest(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="0")


def test_negative_price_raises():
    with pytest.raises(ValidationError, match="greater than 0"):
        OrderRequest(
            symbol="BTCUSDT", side="BUY", order_type="LIMIT", quantity="0.001", price="-100"
        )


def test_zero_price_raises():
    with pytest.raises(ValidationError):
        OrderRequest(
            symbol="BTCUSDT", side="BUY", order_type="LIMIT", quantity="0.001", price="0"
        )


def test_symbol_too_short_raises():
    with pytest.raises(ValidationError, match="too short"):
        OrderRequest(symbol="BT", side="BUY", order_type="MARKET", quantity="0.001")


def test_symbol_with_special_chars_raises():
    with pytest.raises(ValidationError, match="alphanumeric"):
        OrderRequest(symbol="BTC-USDT", side="BUY", order_type="MARKET", quantity="0.001")


def test_market_price_not_required():
    """MARKET orders must succeed even when price is omitted."""
    req = OrderRequest(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="0.001")
    assert req.price is None
