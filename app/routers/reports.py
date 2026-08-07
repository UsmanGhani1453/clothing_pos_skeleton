from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime, date
import csv
import io
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

    total_revenue = 0.0
    total_profit = 0.0
    sales_data = []

    for s in sales:
        total_revenue += s.total_amount
        sale_cost = 0.0
        
        # Calculate the base cost for all items in this specific sale
        for item in s.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            # If the product was deleted from inventory, default the cost to 0
            unit_cost = product.cost_price if product else 0.0
            sale_cost += (unit_cost * item.quantity)
        
        # Profit is the final sale total (after discounts) minus the base cost
        sale_profit = s.total_amount - sale_cost
        total_profit += sale_profit

        sales_data.append({
            "id": s.id,
            "invoice_no": s.invoice_no,
            "total_amount": s.total_amount,
            "profit": sale_profit,
            "payment_method": s.payment_method,
            "created_at": s.created_at.isoformat(),
        })
        
    total_orders = len(sales)

    return {
        "start": str(start),
        "end": str(end),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_profit": total_profit,
        "sales": sales_data,
    }

@router.get("/export")
def export_sales(
    start: date = Query(default=None),
    end: date = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_owner),
):
    """Exports sales data within the date range as a CSV file."""
    if not start:
        start = date.today()
    if not end:
        end = date.today()

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    sales = db.query(models.Sale).filter(
        models.Sale.created_at >= start_dt,
        models.Sale.created_at <= end_dt,
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow(["Invoice No", "Date", "Total Amount", "Profit", "Payment Method", "Cashier", "Customer ID"])

    for s in sales:
        sale_cost = 0.0
        for item in s.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            unit_cost = product.cost_price if product else 0.0
            sale_cost += (unit_cost * item.quantity)
        
        profit = s.total_amount - sale_cost
        
        # Write individual sale data
        writer.writerow([
            s.invoice_no,
            s.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            f"{s.total_amount:.2f}",
            f"{profit:.2f}",
            s.payment_method.capitalize(),
            s.cashier,
            s.customer_id or ""
        ])

    csv_content = output.getvalue()
    output.close()

    headers = {
        "Content-Disposition": f"attachment; filename=sales_report_{start}_to_{end}.csv"
    }
    
    return Response(content=csv_content, media_type="text/csv", headers=headers)