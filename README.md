# Clothing Shop POS

A lightweight, full-stack Point of Sale (POS) desktop application designed for clothing retailers. Built with a modern Python stack, this application combines the performance of FastAPI with a seamless desktop experience powered by PyWebView.

## 🚀 Features

* **Inventory Management:** Add, edit, and track clothing items (by category, size, color, and barcode).
* **Billing & Cart:** Intuitive checkout process with discount handling, multiple payment methods (Cash, Card, Easypaisa, JazzCash), and barcode scanner support.
* **Receipt Generation:** Automatically generate and export PDF receipts optimized for 80mm thermal printers.
* **Reporting:** View daily, weekly, and monthly sales summaries and track revenue.
* **Role-Based Access:** Secure operations with distinct `Owner` and `Cashier` user roles.

## 🛠️ Tech Stack

* **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Local Server:** Uvicorn
* **Database:** SQLite (via SQLAlchemy)
* **Desktop Container:** [PyWebView](https://pywebview.flowrl.com/) (using PyQt5/QtWebEngine on Linux, EdgeHTML/CEF on Windows)
* **Templating:** Jinja2 (HTML/CSS/Vanilla JS)
* **PDF Generation:** ReportLab

## 💻 Local Setup & Development

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Environment Setup
Clone the repository and set up a virtual environment:

```bash
# Create and activate virtual environment (Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Install PyWebView desktop dependencies (Linux/Ubuntu specific)
pip install qtpy PyQt5 PyQtWebEngine
```

### 3. Running the Application

**As a desktop app** (opens in its own window via PyWebView):
```bash
python main.py
```

**As a plain web app** (useful if you don't have PyQt5/a display, or are developing on a server/container):
```bash
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000 in your browser.

On first run, a default **Owner** account is created automatically:
* Username: `admin`
* Password: `admin123`

⚠️ Change this password (or create your own owner account and delete `admin`) before using this in a real shop — see the **Users** page.

### 4. Optional: Load Sample Data
To try the app with some sample products and customers instead of an empty inventory:
```bash
python seed_data.py
```
This is safe to re-run — it skips anything that already exists (matched by barcode/phone) instead of creating duplicates.

### 5. No barcode scanner or receipt printer yet?
You don't need either to use the app:
* **Scanner:** the "Find Product" search box on the Billing page works as a normal text search too — just type a product name or barcode number and press Enter/click Add. A real barcode scanner is just a keyboard emulator, so it'll work automatically once you plug one in — no config needed.
* **Printer:** every sale still generates a receipt. Instead of clicking "Print Receipt" (which opens your browser's print dialog), click **"Download PDF"** to save/share the receipt without needing a thermal printer.

## 📦 Packaging as a Standalone Executable

To compile the application into a single, self-contained executable file (no separate folder of DLLs/libraries to keep alongside it — it's safe to copy or move on its own), use the included `ClothingShopPOS.spec`. First, ensure PyInstaller is installed:
```bash
pip install pyinstaller
```

Then, from the project root (same command on Linux, macOS, and Windows — the spec file already encodes the platform-specific `--add-data` separators and hidden imports):

```bash
pyinstaller ClothingShopPOS.spec
```

The compiled executable will be a single file at `dist/ClothingShopPOS` (or `dist/ClothingShopPOS.exe` on Windows). This one file is fully portable — you can copy, move, or rename it on its own and it'll still run, since everything it needs is packed inside it. (The `--onefile`-style build does mean every launch unpacks itself to a temp folder first, so startup is a couple seconds slower than a bare Python process — this is normal.)

⚠️ If you ever edit the app's dependencies, hidden imports, or bundled data (`app/templates`, `app/static`), update `ClothingShopPOS.spec` to match rather than passing flags on the command line, so the two don't drift out of sync.

## 🔌 API Endpoint Reference

All endpoints (except login) require an active session cookie (log in via the UI or `POST /api/auth/login` first).

| Feature | Prefix | Notes |
|---|---|---|
| Auth | `/api/auth` | `POST /login`, `POST /logout`, `GET /me`, owner-only `GET/POST /users`, `DELETE /users/{id}` |
| Products / Inventory | `/api/products` | `GET /` (supports `?search=`, matches name **or** barcode), `POST /`, `GET/PUT/DELETE /{id}`, `GET /low-stock?threshold=5` |
| Sales / Billing | `/api/sales` | `POST /` (create sale), `GET /` (last 200), `GET /{id}` |
| Customers / Udhar | `/api/customers` | `GET /`, `POST /`, `GET /dues`, `GET /{id}/ledger`, `POST /{id}/pay?amount=` |
| Reports | `/api/reports` | `GET /summary?start=YYYY-MM-DD&end=YYYY-MM-DD` (owner only) |
| Settings | `/api/settings` | `GET /`, `PUT /` (owner only, shop name/address/phone on receipts) |

Product bodies use `sale_price` / `cost_price` / `stock_qty` field names (not `price`/`quantity`) — see `app/schemas.py`.

## 🐛 Bugs Fixed

A few real issues were found and fixed while exercising the UI/JS end-to-end:

1. **Barcode scanning was completely broken.** The product search endpoint only matched against product *name*, so scanning or typing a barcode into the Billing search box always returned zero results. Fixed to match name **or** barcode.
2. **Adding a duplicate barcode crashed the server (500 error)** instead of showing a friendly message. Now returns a proper `400` with "A product with this barcode already exists."
3. **Adding a customer with a phone number already in use crashed the server (500 error).** Now returns a `400` with a clear message.
4. **Recording an Udhar/Khata payment larger than the customer's balance silently drove their balance negative** with no warning. Now rejected with a `400` explaining the payment exceeds what's owed.

## 🗄️ Database Persistence Note

For production builds, the SQLite database (`shop.db`) is configured to be saved in a persistent user directory (e.g., `~/.clothing_pos/shop.db` or `%USERPROFILE%\.clothing_pos\shop.db`). This ensures that inventory and sales data are not lost when the application restarts or when running from a packaged executable.
