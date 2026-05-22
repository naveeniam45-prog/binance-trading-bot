#!/usr/bin/env python3
"""CLI entry point — run with: python cli.py [COMMAND] [OPTIONS]"""

from typing import Optional

import typer
from pydantic import ValidationError
from rich.prompt import Confirm, Prompt

from bot.client import BinanceFuturesClient
from bot.exceptions import APIError, AuthenticationError, NetworkError, TradingBotError
from bot.orders import OrderResponse, place_order
from bot.utils import (
    console,
    display_balance,
    display_banner,
    display_error,
    display_order_response,
    display_order_summary,
)
from bot.validators import OrderRequest

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot — place MARKET and LIMIT orders via CLI.",
    add_completion=False,
    pretty_exceptions_enable=False,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _get_client() -> BinanceFuturesClient:
    try:
        return BinanceFuturesClient()
    except AuthenticationError as exc:
        display_error(str(exc))
        raise typer.Exit(code=1) from exc


def _build_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> Optional[OrderRequest]:
    try:
        return OrderRequest(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=str(quantity),
            price=str(price) if price is not None else None,
        )
    except ValidationError as exc:
        for error in exc.errors():
            display_error(error["msg"])
        return None


def _execute_order(request: OrderRequest, client: BinanceFuturesClient) -> Optional[OrderResponse]:
    try:
        return place_order(request, client)
    except APIError as exc:
        display_error(f"Binance API Error (code {exc.error_code}): {exc}")
    except NetworkError as exc:
        display_error(f"Network Error: {exc}")
    except TradingBotError as exc:
        display_error(str(exc))
    return None


# ---------------------------------------------------------------------------
# place-order command
# ---------------------------------------------------------------------------


@app.command("place-order")
def place_order_cmd(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Option(..., "--side", help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="MARKET or LIMIT"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (required for LIMIT orders)"),
) -> None:
    """Place a MARKET or LIMIT futures order on Binance Testnet."""
    request = _build_request(symbol, side, order_type, quantity, price)
    if request is None:
        raise typer.Exit(code=1)

    display_order_summary(request)

    client = _get_client()
    response = _execute_order(request, client)
    if response is None:
        raise typer.Exit(code=1)

    display_order_response(response)


# ---------------------------------------------------------------------------
# Interactive menu command
# ---------------------------------------------------------------------------


@app.command("menu")
def interactive_menu() -> None:
    """Launch the interactive trading menu (bonus feature)."""
    display_banner()

    client = _get_client()

    while True:
        console.print("[bold cyan]Main Menu[/bold cyan]")
        console.print("  [bold white]1[/bold white]  Place Market Order")
        console.print("  [bold white]2[/bold white]  Place Limit Order")
        console.print("  [bold white]3[/bold white]  View Account Balance")
        console.print("  [bold white]4[/bold white]  Exit\n")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])

        if choice == "1":
            _menu_market_order(client)
        elif choice == "2":
            _menu_limit_order(client)
        elif choice == "3":
            _menu_balance(client)
        else:
            console.print("[yellow]Goodbye![/yellow]\n")
            raise typer.Exit()


def _menu_market_order(client: BinanceFuturesClient) -> None:
    symbol = Prompt.ask("Symbol", default="BTCUSDT").upper().strip()
    side = Prompt.ask("Side", choices=["BUY", "SELL"])
    raw_qty = Prompt.ask("Quantity")

    request = _build_request(symbol, side, "MARKET", float(raw_qty), None)
    if request is None:
        return

    display_order_summary(request)
    if not Confirm.ask("Confirm order?"):
        console.print("[dim]Order cancelled.[/dim]\n")
        return

    response = _execute_order(request, client)
    if response:
        display_order_response(response)


def _menu_limit_order(client: BinanceFuturesClient) -> None:
    symbol = Prompt.ask("Symbol", default="BTCUSDT").upper().strip()
    side = Prompt.ask("Side", choices=["BUY", "SELL"])
    raw_qty = Prompt.ask("Quantity")
    raw_price = Prompt.ask("Limit Price")

    request = _build_request(symbol, side, "LIMIT", float(raw_qty), float(raw_price))
    if request is None:
        return

    display_order_summary(request)
    if not Confirm.ask("Confirm order?"):
        console.print("[dim]Order cancelled.[/dim]\n")
        return

    response = _execute_order(request, client)
    if response:
        display_order_response(response)


def _menu_balance(client: BinanceFuturesClient) -> None:
    try:
        balances = client.get_account_balance()
        display_balance(balances)
    except TradingBotError as exc:
        display_error(str(exc))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app()
