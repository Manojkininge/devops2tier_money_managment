from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:

    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    def create_transaction(self, transaction: Transaction):

        transaction.validate()

        return self.transaction_repository.create(transaction)

    def get_all_transactions(self):

        return self.transaction_repository.find_all()

    def get_transaction(self, transaction_id):

        if transaction_id <= 0:
            raise ValueError("Transaction ID must be greater than 0")

        return self.transaction_repository.find_by_id(transaction_id)

    def update_transaction(self, transaction: Transaction):

        transaction.validate()

        if transaction.id is None:
            raise ValueError("Transaction ID is required for update")

        return self.transaction_repository.update(transaction)

    def delete_transaction(self, transaction_id):

        if transaction_id <= 0:
            raise ValueError("Transaction ID must be greater than 0")

        return self.transaction_repository.delete(transaction_id)