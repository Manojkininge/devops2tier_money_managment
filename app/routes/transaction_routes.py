from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from app.models.transaction import Transaction
from app.services.transaction_service import TransactionService


def create_transaction_blueprint(
    transaction_service: TransactionService
):

    blueprint = Blueprint(
        "transactions",
        __name__,
        url_prefix="/api/transactions"
    )

    @blueprint.post("")
    def create_transaction():

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Request body must contain JSON"
            }), 400

        try:
            transaction = _build_transaction(data)

            saved_transaction = (
                transaction_service.create_transaction(transaction)
            )

            return jsonify(saved_transaction.to_dict()), 201

        except (ValueError, InvalidOperation) as error:

            return jsonify({
                "error": str(error)
            }), 400

    @blueprint.get("")
    def get_all_transactions():

        transactions = (
            transaction_service.get_all_transactions()
        )

        return jsonify([
            transaction.to_dict()
            for transaction in transactions
        ]), 200

    @blueprint.get("/<int:transaction_id>")
    def get_transaction(transaction_id):

        try:
            transaction = (
                transaction_service.get_transaction(
                    transaction_id
                )
            )

            if transaction is None:

                return jsonify({
                    "error": "Transaction not found"
                }), 404

            return jsonify(
                transaction.to_dict()
            ), 200

        except ValueError as error:

            return jsonify({
                "error": str(error)
            }), 400

    @blueprint.put("/<int:transaction_id>")
    def update_transaction(transaction_id):

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "error": "Request body must contain JSON"
            }), 400

        try:

            transaction = _build_transaction(data)

            transaction.id = transaction_id

            updated_transaction = (
                transaction_service.update_transaction(
                    transaction
                )
            )

            if updated_transaction is None:

                return jsonify({
                    "error": "Transaction not found"
                }), 404

            return jsonify(
                updated_transaction.to_dict()
            ), 200

        except (ValueError, InvalidOperation) as error:

            return jsonify({
                "error": str(error)
            }), 400

    @blueprint.delete("/<int:transaction_id>")
    def delete_transaction(transaction_id):

        try:

            deleted = (
                transaction_service.delete_transaction(
                    transaction_id
                )
            )

            if not deleted:

                return jsonify({
                    "error": "Transaction not found"
                }), 404

            return jsonify({
                "message": "Transaction deleted successfully",
                "id": transaction_id
            }), 200

        except ValueError as error:

            return jsonify({
                "error": str(error)
            }), 400

    return blueprint


def _build_transaction(data):

    required_fields = [
        "transaction_type",
        "amount",
        "category",
        "transaction_date",
        "payment_method"
    ]

    for field in required_fields:

        if field not in data:

            raise ValueError(
                f"Missing required field: {field}"
            )

    try:

        amount = Decimal(str(data["amount"]))

    except (InvalidOperation, TypeError):

        raise ValueError(
            "Amount must be a valid number"
        )

    try:

        transaction_date = date.fromisoformat(
            data["transaction_date"]
        )

    except (TypeError, ValueError):

        raise ValueError(
            "transaction_date must use YYYY-MM-DD format"
        )

    return Transaction(
        data["transaction_type"],
        amount,
        data["category"],
        data.get("description"),
        transaction_date,
        data["payment_method"]
    )