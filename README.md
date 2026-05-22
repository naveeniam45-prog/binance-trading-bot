# Binance Futures Testnet Trading Bot

A production-quality CLI trading bot for **Binance Futures Testnet (USDT-M)**, built with Python 3.12.

---

## Features

- Place **MARKET** and **LIMIT** orders on Binance Futures Testnet
- Support **BUY** and **SELL** sides
- Input validation via **Pydantic v2** with clear error messages
- Structured logging to a **rotating log file**
- Beautiful terminal output with **Rich** tables and panels
- **Interactive menu** mode (bonus feature)
- View **account balance**
- Full **exception handling** — API errors, network failures, invalid input
- **Pytest** test suite for validators and order logic

---

## Tech Stack

| Library | Purpose |
|---|---|
| `python-binance` | Binance API client |
| `Typer` | CLI framework |
| `Rich` | Terminal output |
| `Pydantic v2` | Input validation |
| `pydantic-settings` | .env loading |
| `python-dotenv` | Environment management |
| `pytest` | Testing |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures API wrapper
│   ├── config.py          # Settings via pydantic-settings
│   ├── exceptions.py      # Custom exception hierarchy
│   ├── logging_config.py  # Rotating file logger
│   ├── orders.py          # Order placement logic
│   ├── utils.py           # Rich display helpers
│   └── validators.py      # Pydantic OrderRequest model
├── logs/
│   └── trading.log        # Sample log output
├── tests/
│   ├── conftest.py
│   ├── test_orders.py
│   └── test_validators.py
├── .env.example
├── .gitignore
├── cli.py                 # CLI entry point
├── README.md
└── requirements.txt
```

---

## Binance Testnet Setup

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Navigate to **API Management** → **Create API**
4. Copy your **API Key** and **Secret Key**

---

## Installation

```bash
# 1. Clone / unzip the project
cd trading_bot

# 2. Create a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Edit .env and paste your testnet API key and secret
```

---

## Environment Setup

Edit `.env`:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_TESTNET=True
```

---

## Running the Bot

### Place a MARKET order

```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a LIMIT order

```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

### Place a MARKET order (sell ETH)

```bash
python cli.py place-order --symbol ETHUSDT --side SELL --type MARKET --quantity 0.1
```

### Launch the interactive menu

```bash
python cli.py menu
```

The menu lets you:
1. Place Market Order
2. Place Limit Order
3. View Account Balance
4. Exit

### Show all commands

```bash
python cli.py --help
python cli.py place-order --help
```

---

## Sample Output

### MARKET Order

```
╭──────────────────────────────╮
│        ORDER SUMMARY         │
├──────────────┬───────────────┤
│ Symbol       │ BTCUSDT       │
│ Side         │ BUY           │
│ Type         │ MARKET        │
│ Quantity     │ 0.001         │
╰──────────────┴───────────────╯

╭──────────────────────────────╮
│        ORDER RESPONSE        │
├──────────────┬───────────────┤
│ Order ID     │ 3947582       │
│ Symbol       │ BTCUSDT       │
│ Side         │ BUY           │
│ Type         │ MARKET        │
│ Status       │ FILLED        │
│ Orig Qty     │ 0.001         │
│ Executed Qty │ 0.001         │
│ Avg Price    │ $64,250.5500  │
╰──────────────┴───────────────╯

╭──────────────────────────────────────╮
│   ✓  Order placed successfully!      │
╰──────────────────────────────────────╯
```

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_validators.py::test_valid_market_buy         PASSED
tests/test_validators.py::test_valid_limit_sell         PASSED
tests/test_validators.py::test_limit_without_price_raises PASSED
...
tests/test_orders.py::test_place_market_order_returns_filled_response PASSED
tests/test_orders.py::test_place_limit_order_returns_new_response     PASSED
...
```

---

## Logging

All API activity is logged to `logs/trading.log` using a `RotatingFileHandler`:

- **Max size:** 10 MB per file
- **Backup files:** 5 rolling files
- **Format:** `YYYY-MM-DD HH:MM:SS | LEVEL | trading_bot | message`

Logged events:
- Client initialisation
- Every order request (symbol, side, type, quantity, price)
- Full API response payload
- Order confirmation (id, status)
- All errors with error code and message

---

## Error Handling

| Scenario | Exception | Behaviour |
|---|---|---|
| Missing / invalid API key | `AuthenticationError` | Red panel + exit 1 |
| Binance API rejection | `APIError` | Red panel with error code |
| Network timeout / no connection | `NetworkError` | Red panel + exit 1 |
| Invalid CLI input | `ValidationError` (Pydantic) | Per-field error message |
| Unexpected exception | `OrderError` | Red panel + exit 1 |

---

## Assumptions

- **Testnet only** — the `BINANCE_TESTNET=True` flag must remain set. No mainnet usage.
- Quantities and prices are accepted as provided; precision must match the symbol's trading rules on the testnet (e.g. BTCUSDT requires quantity steps of 0.001).
- LIMIT orders use **GTC** (Good Till Cancelled) as `timeInForce` by default.
- The `avgPrice` field shows `N/A` for LIMIT orders that are not yet filled (status `NEW`).
- Log files are written relative to the working directory where `cli.py` is invoked.
