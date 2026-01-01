import datetime as _dt
import sqlalchemy as _sql
import database as _db
import sqlalchemy.orm as _orm
from datetime import datetime, timezone

class User(_db.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, nullable=False, index=True, unique=True)
    hashed_password = _sql.Column(_sql.String, nullable=False)
    date_created = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    categories = _orm.relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = _orm.relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = _orm.relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    recurring_transactions = _orm.relationship("RecurringTransaction", back_populates="user", cascade="all, delete-orphan")

class Category(_db.Base):
    __tablename__ = "categories"
    
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    name = _sql.Column(_sql.String, nullable=False)
    type = _sql.Column(_sql.String, nullable=False)  # 'income' or 'expense'
    color = _sql.Column(_sql.String, default="#3B82F6")  # hex color for UI
    icon = _sql.Column(_sql.String, nullable=True)  # icon name/emoji
    is_default = _sql.Column(_sql.Boolean, default=False)
    created_at = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = _orm.relationship("User", back_populates="categories")
    transactions = _orm.relationship("Transaction", back_populates="category")
    budgets = _orm.relationship("Budget", back_populates="category")
    
    __table_args__ = (
        _sql.UniqueConstraint("user_id", "name", "type", name="uq_user_category_type"),
        _sql.Index("idx_category_user_type", "user_id", "type"),
    )

class Transaction(_db.Base):
    __tablename__ = "transactions"
    
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    category_id = _sql.Column(_sql.Integer, _sql.ForeignKey("categories.id"), nullable=False)
    
    amount = _sql.Column(_sql.Float, nullable=False)
    type = _sql.Column(_sql.String, nullable=False)  # 'income' or 'expense'
    description = _sql.Column(_sql.String, nullable=True)
    date = _sql.Column(_sql.Date, nullable=False)
    
    # Optional fields
    receipt_url = _sql.Column(_sql.String, nullable=True)  # path to uploaded receipt
    notes = _sql.Column(_sql.Text, nullable=True)
    
    # Metadata
    created_at = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Link to recurring transaction if applicable
    recurring_transaction_id = _sql.Column(_sql.Integer, _sql.ForeignKey("recurring_transactions.id"), nullable=True)
    
    # Relationships
    user = _orm.relationship("User", back_populates="transactions")
    category = _orm.relationship("Category", back_populates="transactions")
    recurring_transaction = _orm.relationship("RecurringTransaction", back_populates="generated_transactions")
    
    __table_args__ = (
        _sql.Index("idx_transaction_user_date", "user_id", "date"),
        _sql.Index("idx_transaction_user_type", "user_id", "type"),
    )

class Budget(_db.Base):
    __tablename__ = "budgets"
    
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    category_id = _sql.Column(_sql.Integer, _sql.ForeignKey("categories.id"), nullable=False)
    
    amount = _sql.Column(_sql.Float, nullable=False)
    period = _sql.Column(_sql.String, nullable=False)  # 'monthly', 'weekly', 'yearly'
    
    # For tracking the period
    start_date = _sql.Column(_sql.Date, nullable=False)
    end_date = _sql.Column(_sql.Date, nullable=True)  # null means ongoing
    
    # Alert settings
    alert_threshold = _sql.Column(_sql.Float, default=80.0)  # Alert at 80% of budget
    alert_enabled = _sql.Column(_sql.Boolean, default=True)
    
    created_at = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = _orm.relationship("User", back_populates="budgets")
    category = _orm.relationship("Category", back_populates="budgets")
    
    __table_args__ = (
        _sql.Index("idx_budget_user_period", "user_id", "start_date", "end_date"),
    )

class RecurringTransaction(_db.Base):
    __tablename__ = "recurring_transactions"
    
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"), nullable=False)
    category_id = _sql.Column(_sql.Integer, _sql.ForeignKey("categories.id"), nullable=False)
    
    amount = _sql.Column(_sql.Float, nullable=False)
    type = _sql.Column(_sql.String, nullable=False)  # 'income' or 'expense'
    description = _sql.Column(_sql.String, nullable=False)
    
    # Recurrence settings
    frequency = _sql.Column(_sql.String, nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    interval = _sql.Column(_sql.Integer, default=1)  # every X days/weeks/months
    start_date = _sql.Column(_sql.Date, nullable=False)
    end_date = _sql.Column(_sql.Date, nullable=True)  # null means no end date
    
    # Next occurrence tracking
    next_occurrence = _sql.Column(_sql.Date, nullable=False)
    
    # Status
    is_active = _sql.Column(_sql.Boolean, default=True)
    
    created_at = _sql.Column(_sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = _orm.relationship("User", back_populates="recurring_transactions")
    category = _orm.relationship("Category")
    generated_transactions = _orm.relationship("Transaction", back_populates="recurring_transaction")
    
    __table_args__ = (
        _sql.Index("idx_recurring_next_occurrence", "is_active", "next_occurrence"),
    )