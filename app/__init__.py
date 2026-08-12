from flask import Flask

from app.database.connection import DatabaseConnection
from app.repositories.transaction_repository import TransactionRepository
from app.services.transaction_service import TransactionService
from app.routes.transaction_routes import create_transaction_blueprint


def create_app():

    app = Flask(__name__)

    database_connection = DatabaseConnection()

    transaction_repository = TransactionRepository(
        database_connection
    )

    transaction_service = TransactionService(
        transaction_repository
    )

    transaction_blueprint = create_transaction_blueprint(
        transaction_service
    )

    app.register_blueprint(transaction_blueprint)

    return app