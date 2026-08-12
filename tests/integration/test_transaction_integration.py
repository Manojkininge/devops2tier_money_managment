from datetime import date
from decimal import Decimal

import pytest

from app.database.connection import DatabaseConnection
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.services.transaction_service import TransactionService


@pytest.fixture
def service():

    database_connection = DatabaseConnection()

    repository = TransactionRepository(
        database_connection
    )

    return TransactionService(repository)


def test_create_and_read_real_mysql(service):

    transaction = Transaction(
        "expense",
        Decimal("777.77"),
        "integration-test",
        "Pytest integration test",
        date(2026, 8, 13),
        "cash"
    )

    saved = service.create_transaction(transaction)

    assert saved.id is not None

    found = service.get_transaction(saved.id)

    assert found is not None
    assert found.id == saved.id
    assert found.amount == Decimal("777.77")
    assert found.category == "integration-test"

    service.delete_transaction(saved.id)

    deleted = service.get_transaction(saved.id)

    assert deleted is None