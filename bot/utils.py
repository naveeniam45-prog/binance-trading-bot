"""Rich-based display helpers — all terminal output lives here."""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.orders import OrderResponse
from bot.validators import OrderRequest

console = Console()


def display_order_summary(request: OrderRequest) -> None:
    """Print a formatted table summarising the order about to be placed."""
    table = Table(title="ORDER SUMMARY", box=box.ROUNDED, highlight=True, show_header=True)
    table.add_column("Field", style="cyan bold", min_width=12)
    table.add_column("Value", style="white")

    side_color = "green" if request.side.value == "BUY" else "red"

    table.add_row("Symbol", request.symbol)
    table.add_row("Side", f"[{side_color} bold]{request.side.value}[/{side_color} bold]")
    table.add_row("Type", request.order_type.value)
    table.add_row("Quantity", str(request.quantity))
    if request.price is not None:
        table.add_row("Price", f"${float(request.price):,.2f}")

    console.print()
    console.print(table)


def display_order_response(response: OrderResponse) -> None:
    """Print a formatted table with the API response details."""
    table = Table(title="ORDER RESPONSE", box=box.ROUNDED, highlight=True, show_header=True)
    table.add_column("Field", style="cyan bold", min_width=14)
    table.add_column("Value", style="white")

    status_color = "green" if response.status in ("FILLED", "NEW", "PARTIALLY_FILLED") else "yellow"
    avg = float(response.avg_price) if response.avg_price else 0.0
    avg_display = f"${avg:,.4f}" if avg > 0 else "[dim]N/A — pending fill[/dim]"

    table.add_row("Order ID", str(response.order_id))
    table.add_row("Symbol", response.symbol)
    table.add_row("Side", response.side)
    table.add_row("Type", response.order_type)
    table.add_row("Status", f"[{status_color} bold]{response.status}[/{status_color} bold]")
    table.add_row("Orig Qty", response.orig_qty)
    table.add_row("Executed Qty", response.executed_qty)
    table.add_row("Avg Price", avg_display)

    console.print(table)
    console.print(
        Panel("[bold green]✓  Order placed successfully![/bold green]", border_style="green")
    )
    console.print()


def display_error(message: str) -> None:
    """Print a styled error panel."""
    console.print(
        Panel(f"[bold red]✗  {message}[/bold red]", title="Error", border_style="red")
    )


def display_balance(balances: list[dict]) -> None:
    """Print a table of non-zero account balances."""
    if not balances:
        console.print("[yellow]No non-zero balances found.[/yellow]")
        return

    table = Table(title="ACCOUNT BALANCE", box=box.ROUNDED, highlight=True)
    table.add_column("Asset", style="cyan bold")
    table.add_column("Total Balance", style="white", justify="right")
    table.add_column("Available Balance", style="green", justify="right")
    table.add_column("Unrealised PnL", style="yellow", justify="right")

    for b in balances:
        table.add_row(
            b.get("asset", "—"),
            b.get("balance", "0"),
            b.get("availableBalance", "0"),
            b.get("crossUnPnl", "0"),
        )

    console.print()
    console.print(table)
    console.print()


def display_banner() -> None:
    """Print the application banner."""
    console.rule("[bold blue]Binance Futures Testnet Trading Bot[/bold blue]")
    console.print(
        "[dim]Testnet only — no real funds at risk[/dim]\n",
        justify="center",
    )
