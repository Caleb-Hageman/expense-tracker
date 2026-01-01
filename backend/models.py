import datetime as _dt
import sqlalchemy as _sql
import database as _db
import sqlalchemy.orm as _orm
from enums import OrderSide, OrderType, OrderStatus

class User(_db.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    username = _sql.Column(_sql.String, nullable=False, index=True, unique=True)
    hashed_password = _sql.Column(_sql.String, index=True)
    date_created = _sql.Column(_sql.DateTime, default=lambda: _dt.datetime.now(_dt.timezone.utc))

    portfolios = _orm.relationship("Portfolio", back_populates="user")
    orders = _orm.relationship("Order", back_populates="user")

class Instrument(_db.Base):
    __tablename__ = "instruments"
    id = _sql.Column(_sql.Integer, primary_key=True)
    symbol = _sql.Column(_sql.String, unique=True, nullable=False, index=True)
    name = _sql.Column(_sql.String, nullable=False)

    prices = _orm.relationship("MarketPrice", back_populates="instrument")


class MarketPrice(_db.Base):
    __tablename__ = "market_prices"

    id = _sql.Column(_sql.Integer, primary_key=True)
    instrument_id = _sql.Column(_sql.Integer, _sql.ForeignKey("instruments.id"), nullable=False)
    price = _sql.Column(_sql.Float, nullable=False)
    timestamp = _sql.Column(_sql.DateTime, default=lambda: _dt.datetime.now(_dt.timezone.utc), index=True)

    instrument = _orm.relationship("Instrument", back_populates="prices")

    __table_args__ = (
        _sql.Index("idx_price_instrument_time", "instrument_id", "timestamp"),
    )

class Portfolio(_db.Base):
    __tablename__ = "portfolios"

    id = _sql.Column(_sql.Integer, primary_key=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    cash_balance = _sql.Column(_sql.Float, nullable=False, default=0.0)
    created_at = _sql.Column(_dt.DateTime, default=lambda: _dt.datetime.now(_dt.timezone.utc))

    user = _orm.relationship("User", back_populates="portfolios")
    positions = _orm.relationship("Position", back_populates="portfolio")
    orders = _orm.relationship("Order", back_populates="portfolio")

class Position(_db.Base):
    __tablename__ = "positions"

    id = _sql.Column(_sql.Integer, primary_key=True)
    portfolio_id = _sql.Column(_sql.Integer, _sql.ForeignKey("portfolios.id"), nullable=False)
    instrument_id = _sql.Column(_sql.Integer, _sql.ForeignKey("instruments.id"), nullable=False)
    quantity = _sql.Column(_sql.Float, nullable=False)
    avg_price = _sql.Column(_sql.Float, nullable=False)

    portfolio = _orm.relationship("Portfolio", back_populates="positions")
    instrument = _orm.relationship("Instrument")

    __table_args__ = (
        _sql.UniqueConstraint("portfolio_id", "instrument_id", name="uq_portfolio_instrument"),
    )

class Order(_db.Base):
    __tablename__ = "orders"

    id = _sql.Column(_sql.Integer, primary_key=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    portfolio_id = _sql.Column(_sql.Integer, _sql.ForeignKey("portfolios.id"), nullable=False)
    instrument_id = _sql.Column(_sql.Integer, _sql.ForeignKey("instruments.id"), nullable=False)

    side = _sql.Column(_sql.Enum(OrderSide), nullable=False)
    order_type = _sql.Column(_sql.Enum(OrderType), nullable=False)
    status = _sql.Column(_sql.Enum(OrderStatus), nullable=False, default=OrderStatus.OPEN)

    price = _sql.Column(_sql.Float)  # nullable for market orders
    quantity = _sql.Column(_sql.Float, nullable=False)
    filled_quantity = _sql.Column(_sql.Float, default=0.0)

    created_at = _sql.Column(_sql.DateTime, default=_sql.datetime.now(_dt.UTC))

    user = _orm.relationship("User", back_populates="orders")
    portfolio = _orm.relationship("Portfolio", back_populates="orders")
    instrument = _orm.relationship("Instrument")

    trades = _orm.relationship("Trade", back_populates="order")

    __table_args__ = (
        _sql.Index("idx_order_book", "instrument_id", "side", "price"),
    )

class Trade(_db.Base):
    __tablename__ = "trades"

    id = _sql.Column(_sql.Integer, primary_key=True)
    order_id = _sql.Column(_sql.Integer, _sql.ForeignKey("orders.id"), nullable=False)
    instrument_id = _sql.Column(_sql.Integer, _sql.ForeignKey("instruments.id"), nullable=False)

    price = _sql.Column(_sql.Float, nullable=False)
    quantity = _sql.Column(_sql.Float, nullable=False)
    timestamp = _sql.Column(_sql.DateTime, default=lambda: _dt.datetime.now(_dt.timezone.utc))

    order = _orm.relationship("Order", back_populates="trades")
    instrument = _orm.relationship("Instrument")

    __table_args__ = (
        _sql.Index("idx_trade_instrument_time", "instrument_id", "timestamp"),
    )
