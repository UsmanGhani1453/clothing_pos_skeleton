from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as mm_unit
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import io

SHOP_NAME = "Your Clothing Shop"
SHOP_ADDRESS = "Main Bazaar, Lahore"

PAGE_WIDTH = 80 * mm_unit  # 80mm thermal roll width
MARGIN = 4 * mm_unit


def generate_receipt_pdf(sale, shop_settings=None) -> bytes:
    """Generate a PDF receipt for the given Sale ORM object, sized for 80mm thermal paper."""
    shop_settings = shop_settings or {}
    shop_name = shop_settings.get("shop_name", SHOP_NAME)
    shop_address = shop_settings.get("shop_address", SHOP_ADDRESS)

    buffer = io.BytesIO()

    # Estimate height dynamically based on number of items
    line_height = 4.2 * mm_unit
    base_height = 55 * mm_unit
    items_height = len(sale.items) * (line_height * 2)
    page_height = base_height + items_height

    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, page_height))
    y = page_height - MARGIN

    def draw_center(text, size=11, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawCentredString(PAGE_WIDTH / 2, y, text)
        y -= size * 0.8 * mm_unit / 2.2

    def draw_row(left, right, size=9, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(MARGIN, y, left)
        c.drawRightString(PAGE_WIDTH - MARGIN, y, right)
        y -= size * 1.3

    def draw_divider():
        nonlocal y
        y -= 2
        c.setDash(1, 2)
        c.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
        c.setDash()
        y -= 6

    draw_center(shop_name, size=13, bold=True)
    draw_center(shop_address, size=8)
    y -= 4
    draw_divider()

    draw_row("Invoice:", sale.invoice_no, size=8)
    draw_row("Date:", sale.created_at.strftime("%d-%b-%Y %I:%M %p"), size=8)
    draw_row("Cashier:", sale.cashier or "-", size=8)
    draw_divider()

    for item in sale.items:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y, item.product_name[:32])
        y -= 10
        draw_row(
            f"{item.quantity} x Rs. {item.unit_price:.0f}",
            f"Rs. {item.subtotal:.0f}",
            size=8,
        )
        y -= 2

    draw_divider()
    subtotal = sale.total_amount + sale.discount
    draw_row("Subtotal:", f"Rs. {subtotal:.0f}", size=9)
    draw_row("Discount:", f"-Rs. {sale.discount:.0f}", size=9)
    y -= 2
    draw_row("TOTAL:", f"Rs. {sale.total_amount:.0f}", size=11, bold=True)
    y -= 4
    draw_row("Payment:", sale.payment_method.capitalize(), size=9)
    draw_divider()

    draw_center("Thank you for shopping with us!", size=8)
    draw_center("No exchange without receipt.", size=8)

    c.save()
    buffer.seek(0)
    return buffer.read()
