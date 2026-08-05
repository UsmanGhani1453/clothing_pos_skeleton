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
To run the application in development mode:
```bash
python main.py
```

## 📦 Packaging as a Standalone Executable

To compile the application into a single executable file without a background terminal, use PyInstaller. First, ensure PyInstaller is installed:
```bash
pip install pyinstaller
```

### For Linux
Run the following build command from the root directory to bundle the application. Note the use of colons (`:`) and backslashes (`\`) for line breaks:

```bash
pyinstaller --name "ClothingShopPOS" \
--windowed \
--add-data "app/templates:app/templates" \
--add-data "app/static:app/static" \
--hidden-import="uvicorn.logging" \
--hidden-import="uvicorn.loops" \
--hidden-import="uvicorn.loops.auto" \
--hidden-import="uvicorn.protocols" \
--hidden-import="uvicorn.protocols.http.auto" \
--hidden-import="uvicorn.protocols.websockets.auto" \
--hidden-import="uvicorn.lifespan.on" \
--hidden-import="uvicorn.lifespan.off" \
main.py
```

### For Windows
Run the following build command from a Windows environment. Note the use of semicolons (`;`) in the `--add-data` flags and carets (`^`) for line breaks in the command prompt:

```bash
pyinstaller --name "ClothingShopPOS" ^
--windowed ^
--add-data "app/templates;app/templates" ^
--add-data "app/static;app/static" ^
--hidden-import="uvicorn.logging" ^
--hidden-import="uvicorn.loops" ^
--hidden-import="uvicorn.loops.auto" ^
--hidden-import="uvicorn.protocols" ^
--hidden-import="uvicorn.protocols.http.auto" ^
--hidden-import="uvicorn.protocols.websockets.auto" ^
--hidden-import="uvicorn.lifespan.on" ^
--hidden-import="uvicorn.lifespan.off" ^
main.py
```

The compiled executable will be located in the `dist/ClothingShopPOS` directory.

## 🗄️ Database Persistence Note

For production builds, the SQLite database (`shop.db`) is configured to be saved in a persistent user directory (e.g., `~/.clothing_pos/shop.db` or `%USERPROFILE%\.clothing_pos\shop.db`). This ensures that inventory and sales data are not lost when the application restarts or when running from a packaged executable.
