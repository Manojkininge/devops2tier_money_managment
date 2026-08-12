from datetime import date
from decimal import Decimal

import pytest

from app.models.transaction import Transaction
from app.services.transaction_service import TransactionService


class FakeTransactionRepository:

    def __init__(self):
        self.transactions = []
        self.next_id = 1

    def create(self, transaction):
        transaction.id = self.next_id
        self.next_id += 1
        self.transactions.append(transaction)
        return transaction

    def find_all(self):
        return self.transactions

    def find_by_id(self, transaction_id):

        for transaction in self.transactions:

            if transaction.id == transaction_id:
                return transaction

        return None

    def update(self, transaction):

        for index, existing in enumerate(self.transactions):

            if existing.id == transaction.id:
                self.transactions[index] = transaction
                return transaction

        return None

    def delete(self, transaction_id):

        for index, transaction in enumerate(self.transactions):

            if transaction.id == transaction_id:
                del self.transactions[index]
                return True

        return False


@pytest.fixture
def service():

    repository = FakeTransactionRepository()

    return TransactionService(repository)


def create_transaction():

    return Transaction(
        "expense",
        Decimal("1000.00"),
        "food",
        "Lunch",
        date(2026, 8, 13),
        "upi"
    )


def test_create_transaction(service):

    transaction = create_transaction()

    saved = service.create_transaction(transaction)

    assert saved.id == 1
    assert saved.transaction_type == "expense"
    assert saved.amount == Decimal("1000.00")


def test_get_all_transactions(service):

    service.create_transaction(create_transaction())

    transactions = service.get_all_transactions()

    assert len(transactions) == 1


def test_get_transaction(service):

    created = service.create_transaction(
        create_transaction()
    )

    found = service.get_transaction(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_missing_transaction(service):

    result = service.get_transaction(999)

    assert result is None


def test_invalid_transaction_type(service):

    transaction = Transaction(
        "wrong",
        Decimal("500.00"),
        "test",
        "Invalid",
        date(2026, 8, 13),
        "cash"
    )

    with pytest.raises(
        ValueError,
        match="Transaction type must be 'income' or 'expense'"
    ):
        service.create_transaction(transaction)


def test_negative_amount(service):

    transaction = Transaction(
        "expense",
        Decimal("-500.00"),
        "test",
        "Invalid amount",
        date(2026, 8, 13),
        "cash"
    )

    with pytest.raises(
        ValueError,
        match="Amount must be greater than zero"
    ):
        service.create_transaction(transaction)


def test_invalid_transaction_id(service):

    with pytest.raises(
        ValueError,
        match="Transaction ID must be greater than 0"
    ):
        service.get_transaction(0)


def test_update_transaction(service):

    transaction = service.create_transaction(
        create_transaction()
    )

    transaction.amount = Decimal("1500.00")

    updated = service.update_transaction(transaction)

    assert updated.amount == Decimal("1500.00")


def test_delete_transaction(service):

    transaction = service.create_transaction(
        create_transaction()
    )

    result = service.delete_transaction(
        transaction.id
    )

    assert result is True
    assert service.get_transaction(transaction.id) is None


def test_delete_missing_transaction(service):

    result = service.delete_transaction(999)

    assert result is False