from datetime import date
from decimal import Decimal

import pytest

from app.models.transaction import Transaction
from app.routes.transaction_routes import create_transaction_blueprint
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
def client():

    repository = FakeTransactionRepository()

    service = TransactionService(repository)

    from flask import Flask

    app = Flask(__name__)

    blueprint = create_transaction_blueprint(service)

    app.register_blueprint(blueprint)

    app.config["TESTING"] = True

    return app.test_client()


def transaction_payload():

    return {
        "transaction_type": "expense",
        "amount": "1000.00",
        "category": "food",
        "description": "Lunch",
        "transaction_date": "2026-08-13",
        "payment_method": "upi"
    }


def test_create_transaction(client):

    response = client.post(
        "/api/transactions",
        json=transaction_payload()
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["transaction_type"] == "expense"
    assert data["amount"] == "1000.00"
    assert data["category"] == "food"


def test_get_all_transactions(client):

    client.post(
        "/api/transactions",
        json=transaction_payload()
    )

    response = client.get(
        "/api/transactions"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["category"] == "food"


def test_get_transaction_by_id(client):

    client.post(
        "/api/transactions",
        json=transaction_payload()
    )

    response = client.get(
        "/api/transactions/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1


def test_get_missing_transaction(client):

    response = client.get(
        "/api/transactions/999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Transaction not found"


def test_update_transaction(client):

    client.post(
        "/api/transactions",
        json=transaction_payload()
    )

    updated_payload = {
        "transaction_type": "expense",
        "amount": "1500.00",
        "category": "food",
        "description": "Dinner",
        "transaction_date": "2026-08-13",
        "payment_method": "upi"
    }

    response = client.put(
        "/api/transactions/1",
        json=updated_payload
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["amount"] == "1500.00"
    assert data["description"] == "Dinner"


def test_delete_transaction(client):

    client.post(
        "/api/transactions",
        json=transaction_payload()
    )

    response = client.delete(
        "/api/transactions/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1
    assert data["message"] == "Transaction deleted successfully"


def test_delete_missing_transaction(client):

    response = client.delete(
        "/api/transactions/999"
    )

    assert response.status_code == 404


def test_invalid_transaction_type(client):

    payload = transaction_payload()

    payload["transaction_type"] = "wrong"

    response = client.post(
        "/api/transactions",
        json=payload
    )

    assert response.status_code == 400

    data = response.get_json()

    assert (
        data["error"]
        == "Transaction type must be 'income' or 'expense'"
    )


def test_negative_amount(client):

    payload = transaction_payload()

    payload["amount"] = "-500.00"

    response = client.post(
        "/api/transactions",
        json=payload
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Amount must be greater than zero"


def test_missing_required_field(client):

    payload = transaction_payload()

    del payload["category"]

    response = client.post(
        "/api/transactions",
        json=payload
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing required field: category"