from enum import Enum


class TransactionType(str, Enum):
    """Type of transaction"""
    INCOME = "income"
    EXPENSE = "expense"


class BudgetPeriod(str, Enum):
    """Budget time period"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurrenceFrequency(str, Enum):
    """Frequency for recurring transactions"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ExportFormat(str, Enum):
    """Export file formats"""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"