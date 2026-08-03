from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from .. import models
from ..database import get_db
from ..auth import require_owner

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
def sales_summary(
    start: date = Query(default=None),
    end: date = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_owner),
):
    if not start:
        start = date.today()
    if not end:
        end = date.today()

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    q = db.query(models.Sale).filter(
        models.Sale.created_at >= start_dt,
        models.Sale.created_at <= end_dt,
    )

    sales = q.all()
    total_revenue = sum(s.total_amount for s in sales)
    total_orders = len(sales)

    return {
        "start": str(start),
        "end": str(end),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "sales": [
            {
                "invoice_no": s.invoice_no,
                "total_amount": s.total_amount,
                "payment_method": s.payment_method,
                "created_at": s.created_at.isoformat(),
            }
            for s in sales
        ],
    }
