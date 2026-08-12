from app.database.connection import DatabaseConnection
from app.models.transaction import Transaction


class TransactionRepository:

    def __init__(self, database_connection: DatabaseConnection):
        self.database_connection = database_connection

    def create(self, transaction):

        connection = self.database_connection.connect()
        cursor = connection.cursor()

        sql = """
            INSERT INTO transactions
            (
                transaction_type,
                amount,
                category,
                description,
                transaction_date,
                payment_method
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            transaction.transaction_type,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.transaction_date,
            transaction.payment_method
        )

        cursor.execute(sql, values)
        connection.commit()

        transaction.id = cursor.lastrowid

        cursor.close()
        self.database_connection.close()

        return transaction

    def find_all(self):

        connection = self.database_connection.connect()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                id,
                transaction_type,
                amount,
                category,
                description,
                transaction_date,
                payment_method,
                created_at,
                updated_at
            FROM transactions
            ORDER BY id
        """

        cursor.execute(sql)

        rows = cursor.fetchall()

        cursor.close()
        self.database_connection.close()

        transactions = []

        for row in rows:

            transaction = Transaction(
                row["transaction_type"],
                row["amount"],
                row["category"],
                row["description"],
                row["transaction_date"],
                row["payment_method"]
            )

            transaction.id = row["id"]
            transaction.created_at = row["created_at"]
            transaction.updated_at = row["updated_at"]

            transactions.append(transaction)

        return transactions


    def find_by_id(self, transaction_id):

        connection = self.database_connection.connect()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                id,
                transaction_type,
                amount,
                category,
                description,
                transaction_date,
                payment_method,
                created_at,
                updated_at
            FROM transactions
            WHERE id = %s
        """

        cursor.execute(sql, (transaction_id,))

        row = cursor.fetchone()

        cursor.close()
        self.database_connection.close()

        if row is None:
            return None

        transaction = Transaction(
            row["transaction_type"],
            row["amount"],
            row["category"],
            row["description"],
            row["transaction_date"],
            row["payment_method"]
        )

        transaction.id = row["id"]
        transaction.created_at = row["created_at"]
        transaction.updated_at = row["updated_at"]

        return transaction

    def update(self, transaction):

        connection = self.database_connection.connect()
        cursor = connection.cursor()

        sql = """
            UPDATE transactions
            SET
                transaction_type = %s,
                amount = %s,
                category = %s,
                description = %s,
                transaction_date = %s,
                payment_method = %s
            WHERE id = %s
        """

        values = (
            transaction.transaction_type,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.transaction_date,
            transaction.payment_method,
            transaction.id
        )

        cursor.execute(sql, values)

        connection.commit()

        rows_updated = cursor.rowcount

        cursor.close()
        self.database_connection.close()

        if rows_updated == 0:
            return None

        return transaction


    def delete(self, transaction_id):

        connection = self.database_connection.connect()
        cursor = connection.cursor()

        sql = """
            DELETE FROM transactions
            WHERE id = %s
        """

        cursor.execute(sql, (transaction_id,))

        connection.commit()

        rows_deleted = cursor.rowcount

        cursor.close()
        self.database_connection.close()

        return rows_deleted > 0
    