"""Tests for bot.orders.place_order — client is fully mocked."""

from unittest.mock import MagicMock

import pytest

from bot.exceptions import APIError, NetworkError
from bot.orders import OrderResponse, place_order
from tests.conftest import LIMIT_RAW_RESPONSE, MARKET_RAW_RESPONSE


# ---------------------------------------------------------------------------
# Market order
# ---------------------------------------------------------------------------


def test_place_market_order_returns_filled_response(market_request):
    client = MagicMock()
    client.create_market_order.return_value = MARKET_RAW_RESPONSE

    result = place_order(market_request, client)

    assert isinstance(result, OrderResponse)
    assert result.order_id == 3947582
    assert result.status == "FILLED"
    assert result.executed_qty == "0.001"
    assert result.avg_price == "64250.55"
    assert result.side == "BUY"
    assert result.order_type == "MARKET"


def test_place_market_order_calls_correct_client_method(market_request):
    client = MagicMock()
    client.create_market_order.return_value = MARKET_RAW_RESPONSE

    place_order(market_request, client)

    client.create_market_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001,
    )
    client.create_limit_order.assert_not_called()


# ---------------------------------------------------------------------------
# Limit order
# ---------------------------------------------------------------------------


def test_place_limit_order_returns_new_response(limit_request):
    client = MagicMock()
    client.create_limit_order.return_value = LIMIT_RAW_RESPONSE

    result = place_order(limit_request, client)

    assert isinstance(result, OrderResponse)
    assert result.order_id == 3947589
    assert result.status == "NEW"
    assert result.executed_qty == "0.000"
    assert result.side == "SELL"
    assert result.order_type == "LIMIT"


def test_place_limit_order_calls_correct_client_method(limit_request):
    client = MagicMock()
    client.create_limit_order.return_value = LIMIT_RAW_RESPONSE

    place_order(limit_request, client)

    client.create_limit_order.assert_called_once_with(
        symbol="ETHUSDT",
        side="SELL",
        quantity=1.0,
        price=3000.0,
    )
    client.create_market_order.assert_not_called()


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------


def test_api_error_propagates(market_request):
    client = MagicMock()
    client.create_market_order.side_effect = APIError("Invalid API key", error_code=-2014)

    with pytest.raises(APIError, match="Invalid API key"):
        place_order(market_request, client)


def test_network_error_propagates(market_request):
    client = MagicMock()
    client.create_market_order.side_effect = NetworkError("Connection timeout")

    with pytest.raises(NetworkError, match="Connection timeout"):
        place_order(market_request, client)


def test_api_error_preserves_error_code(market_request):
    client = MagicMock()
    client.create_market_order.side_effect = APIError("Bad request", error_code=-1102)

    with pytest.raises(APIError) as exc_info:
        place_order(market_request, client)

    assert exc_info.value.error_code == -1102


# ---------------------------------------------------------------------------
# Response field mapping
# ---------------------------------------------------------------------------


def test_response_raw_is_preserved(market_request):
    client = MagicMock()
    client.create_market_order.return_value = MARKET_RAW_RESPONSE

    result = place_order(market_request, client)

    assert result.raw == MARKET_RAW_RESPONSE


def test_avg_price_falls_back_to_price_field(limit_request):
    """When avgPrice is '0', the 'price' field is used instead."""
    raw = {**LIMIT_RAW_RESPONSE, "avgPrice": "0", "price": "3000"}
    client = MagicMock()
    client.create_limit_order.return_value = raw

    result = place_order(limit_request, client)

    assert result.avg_price == "3000"
