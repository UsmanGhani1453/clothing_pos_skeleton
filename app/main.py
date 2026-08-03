from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import os
import secrets

from . import models
from .database import engine, get_db, SessionLocal
from .routers import inventory, billing, reports, auth as auth_router, settings as settings_router
from .auth import get_current_user_optional, get_current_user, ensure_default_owner
from .receipts import generate_receipt_pdf
from .settings import get_all_settings

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Seed a default owner account on first run
_db = SessionLocal()
try:
    ensure_default_owner(_db)
finally:
    _db.close()

app = FastAPI(title="Clothing Shop POS")

# Session cookie secret - randomized per run is fine for a single-machine offline app.
# (Sessions reset on restart; acceptable for a shop POS used on one PC.)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.include_router(inventory.router)
app.include_router(billing.router)
app.include_router(reports.router)
app.include_router(auth_router.router)
app.include_router(settings_router.router)


@app.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(request, "login.html", {})


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != "owner":
        return RedirectResponse(url="/billing")
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})


@app.get("/billing")
def billing_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "billing.html", {"user": user})


@app.get("/inventory")
def inventory_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != "owner":
        return RedirectResponse(url="/billing")
    return templates.TemplateResponse(request, "inventory.html", {"user": user})


@app.get("/reports")
def reports_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != "owner":
        return RedirectResponse(url="/billing")
    return templates.TemplateResponse(request, "reports.html", {"user": user})


@app.get("/users")
def users_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != "owner":
        return RedirectResponse(url="/billing")
    return templates.TemplateResponse(request, "users.html", {"user": user})


@app.get("/settings")
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != "owner":
        return RedirectResponse(url="/billing")
    return templates.TemplateResponse(request, "settings.html", {"user": user})


@app.get("/receipt/{sale_id}")
def receipt_page(
    sale_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    shop_settings = get_all_settings(db)
    return templates.TemplateResponse(
        request,
        "receipt.html",
        {
            "sale": sale,
            "shop_name": shop_settings["shop_name"],
            "shop_address": shop_settings["shop_address"],
        },
    )


@app.get("/api/sales/{sale_id}/receipt.pdf")
def receipt_pdf(
    sale_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    shop_settings = get_all_settings(db)
    pdf_bytes = generate_receipt_pdf(sale, shop_settings)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{sale.invoice_no}.pdf"'},
    )
