from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from src.core_api.models.transaction import Transaction
from src.core_api.db.transaction_db import TransactionDatabase

CURRENT_RAM_PER_SEC = 0.05 # can be change
CURRENT_CPU_PER_SEC = 0.1


class TransactionService:
    def __init__(self, db: Optional[TransactionDatabase] = None):
        self.db = db or TransactionDatabase()

    def _filter_transactions(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Transaction]:
        return self.db.list_transactions(
            job_id=job_id,
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )

    def get_total_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        total: float = sum(t.total_cost for t in transactions)
        return total

    def get_paid_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        total: float = sum(t.total_cost for t in transactions if t.status == "paid")
        return total

    def get_pending_expenses(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        return sum(t.total_cost for t in transactions if t.status == "pending")

    def get_total_earnings(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        compare_start: Optional[datetime] = None,
        compare_end: Optional[datetime] = None,
    ) -> Tuple[float, Optional[float]]:
        current_earnings = self.get_paid_expenses(job_id, start_time, end_time)
        rate_change = None
        if compare_start and compare_end:
            previous_earnings = self.get_paid_expenses(job_id, compare_start, compare_end)
            if previous_earnings > 0:
                rate_change = ((current_earnings - previous_earnings) / previous_earnings) * 100
            elif current_earnings > 0:
                rate_change = 100.0
            else:
                rate_change = None
                return current_earnings, rate_change
        return current_earnings, None

    def get_earning_rate(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = self._filter_transactions(job_id, start_time, end_time)
        total_earnings = sum(t.total_cost for t in transactions if t.status == "paid")
        total_time = sum(t.execution_time for t in transactions)

        if total_time == 0:
            return 0.0
        return total_earnings / total_time

    def get_average_earnings(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        transactions = [t for t in self._filter_transactions(job_id, start_time, end_time) if t.status == "paid"]
        if not transactions:
            return 0.0
        total_earnings = sum(t.total_cost for t in transactions)
        return total_earnings / len(transactions)

    def get_transaction_history(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Transaction]:
        return self.db.list_transactions(
            job_id=job_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

    def get_current_cost_ram_per_gb_sec(self) -> float:
        return CURRENT_RAM_PER_SEC

    def get_current_cost_cpu_per_core_sec(self) -> float:
        return CURRENT_CPU_PER_SEC
