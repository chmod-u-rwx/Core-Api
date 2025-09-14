from datetime import datetime
from uuid import UUID
from typing import List, Optional, Tuple
from src.core_api.models.transaction import Transaction
from src.core_api.db.transaction_db import TransactionDatabase

COST_RAM_PER_SECOND = 0.05
COST_CPU_PER_SECOND = 0.10

class TransactionService:
    def __init__(self, db: TransactionDatabase):
        self.db = db

    def _filter_transactions(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Transaction]:
        return self.db.list_transactions(
            job_id=job_id,
            start_time=start_time,
            end_time=end_time
        )

    def get_total_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        return sum(t.total_cost for t in transactions)

    def get_paid_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        return sum(t.total_cost for t in transactions if getattr(t, "paid", True))

    def get_pending_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        return sum(t.total_cost for t in transactions if not getattr(t, "paid", False))

    def get_total_earnings(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        return self.get_total_expenses(job_id, start_time, end_time)

    def get_average_earnings(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        if not transactions:
            return 0.0
        return sum(t.total_cost for t in transactions) / len(transactions)

    def get_earning_rate(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        if not transactions or not start_time or not end_time:
            return 0.0
        hours = (end_time - start_time).total_seconds() / 3600
        return sum(t.total_cost for t in transactions) / hours

    def get_transaction_history(
        self,
        job_id: Optional[UUID]= None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Transaction]:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        sorted_tx = sorted(transactions, key=lambda t: t.timestamp, reverse=True)
        return sorted_tx[:limit]

    @staticmethod
    def get_current_costs() -> Tuple[float, float]:
        return COST_RAM_PER_SECOND, COST_CPU_PER_SECOND
