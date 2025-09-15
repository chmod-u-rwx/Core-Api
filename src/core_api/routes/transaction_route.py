from fastapi import APIRouter, HTTPException
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from src.core_api.services.transaction_service import TransactionService
from src.core_api.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])
service = TransactionService()

@router.post("/", response_model=Transaction)
def create_transaction(transaction: Transaction):
    try:
        return service.db.create(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: UUID):
    try:
        return service.db.get_by_id(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history", response_model=List[Transaction])
def get_transaction_history(
    job_id: Optional[UUID] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
):
    try:
        return service.get_transaction_history(job_id, start_time, end_time, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def get_summary(
    job_id: Optional[UUID] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    try:
        return {
            "total_expenses": service.get_total_expenses(job_id, start_time, end_time),
            "paid_expenses": service.get_paid_expenses(job_id, start_time, end_time),
            "pending_expenses": service.get_pending_expenses(job_id, start_time, end_time),
            "earning_rate": service.get_earning_rate(job_id, start_time, end_time),
            "average_earnings": service.get_average_earnings(job_id, start_time, end_time),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
