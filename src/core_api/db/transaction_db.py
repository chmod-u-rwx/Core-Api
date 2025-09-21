from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from src.core_api.config import DATABASE_NAME
from src.core_api.db.connection import get_mongo_client
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection
from src.core_api.models.transaction import Transaction

class TransactionNotFoundException(Exception):
    ...

class TransactionDatabase:
    def __init__(self) -> None:
        try:
            self.client = get_mongo_client()
            self.db: Database[Any] = self.client[DATABASE_NAME]
            self.collection: Collection[Any] = self.db["transactions"]
            self._create_indexes()
        except PyMongoError as e:
            raise RuntimeError(f"Database initialization failed: {e}")

    def _create_indexes(self) -> None:
        try: 
            self.collection.create_index(
                [("transaction_id", 1)],
                name="idx_transaction_id",
                unique=True,
            )
            self.collection.create_index(
                [("request_id", 1)],
                name="idx_request_id"
            )
            self.collection.create_index(
                [("job_id", 1)],
                name="idx_job_id"
            )
            self.collection.create_index(
                [("worker_id", 1)],
                name="idx_worker_id"
            )
            self.collection.create_index(
                [("timestamp", 1)],
                name="idx_timestamp",
            )
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")

    def create(self, transaction: Transaction) -> Transaction:
        doc = transaction.model_dump(mode="json")
        
        doc["transaction_id"] = str(transaction.transaction_id)
        doc["request_id"] = str(transaction.request_id)
        doc["job_id"] = str(transaction.job_id)
        doc["worker_id"] = str(transaction.worker_id)
        doc["timestamp"] = transaction.timestamp

        try:
            result = self.collection.insert_one(doc)
            if not result.inserted_id:
                raise RuntimeError("Failed to insert transaction")

            inserted = self.collection.find_one({"_id": result.inserted_id})
            if not inserted:
                raise RuntimeError("Inserted transaction not found")

            inserted.pop("_id", None)
            return Transaction(**inserted)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to create transaction: {e}")

    def get_by_id(self, transaction_id: UUID) -> Transaction:

        doc = self.collection.find_one({"transaction_id": str(transaction_id)})
        if not doc:
            raise TransactionNotFoundException(f"Transaction {transaction_id} not found")
        
        doc.pop("_id", None)
        return Transaction(**doc)

    def get_by_job_id(self, job_id: UUID) -> List[Transaction]:
        docs = self.collection.find({"job_id": str(job_id)})
        transactions: List[Transaction] = []
        
        for doc in docs:
            doc.pop("_id", None)
            transactions.append(Transaction(**doc))
        
        return transactions

    def list_transactions(
        self,
        job_id: Optional[UUID] = None,
        request_id: Optional[UUID] = None,
        worker_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Transaction]:
        query: dict[str, Any] = {}

        if job_id:
            query["job_id"] = str(job_id)

        if request_id:
            query["request_id"] = str(request_id)

        if worker_id:
            query["worker_id"] = str(worker_id)

        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time

        docs = list(self.collection.find(query).limit(limit))
        transactions: List[Transaction] = []
        
        for doc in docs:
            doc.pop("_id", None)
            transactions.append(Transaction(**doc))

        return transactions

    def delete(self, transaction_id: UUID) -> bool:
        try:
            result = self.collection.delete_one({"transaction_id": str(transaction_id)})
            if result.deleted_count == 0:
                raise TransactionNotFoundException(f"Transaction with id {transaction_id} not found")
            return True
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete transaction: {e}")
