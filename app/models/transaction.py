from datetime import date, datetime
from decimal import Decimal


class Transaction:

    def __init__(
        self,
        transaction_type: str,
        amount: Decimal,
        category: str,
        description: str,
        transaction_date: date,
        payment_method: str,
        transaction_id: int | None = None
    ):
        self.id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.category = category
        self.description = description
        self.transaction_date = transaction_date
        self.payment_method = payment_method
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def validate(self):
        if self.transaction_type not in ("income", "expense"):
            raise ValueError(
                "Transaction type must be 'income' or 'expense'"
            )

        if self.amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero")

        if not self.category.strip():
            raise ValueError("Category cannot be empty")

        if not self.payment_method.strip():
            raise ValueError("Payment method cannot be empty")

    def is_income(self):
        return self.transaction_type == "income"

    def is_expense(self):
        return self.transaction_type == "expense"

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat(),
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

