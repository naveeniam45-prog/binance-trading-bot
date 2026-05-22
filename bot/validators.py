"""Pydantic models for validating CLI input before it reaches the API layer."""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None

    @field_validator("side", "order_type", mode="before")
    @classmethod
    def normalise_to_upper(cls, v: object) -> object:
        if isinstance(v, str):
            return v.upper().strip()
        return v

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) < 3:
            raise ValueError(f"Symbol '{v}' is too short — minimum 3 characters (e.g. BTCUSDT)")
        if not v.isalnum():
            raise ValueError(f"Symbol '{v}' is invalid — must be alphanumeric (e.g. BTCUSDT)")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @model_validator(mode="after")
    def price_required_for_limit(self) -> "OrderRequest":
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("Price is required for LIMIT orders")
        return self
