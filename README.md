# 🚀 API Automation Framework — REST & SOAP

A Python-based API test automation framework that supports both **REST** and **SOAP** requests, with Excel/JSON input and a styled Excel report as output. Can be packaged as a standalone Windows `.exe`.

---

## ✨ Features

- ✅ **REST & SOAP** test execution in a single run
- ✅ **Serial & Parallel** execution modes
- ✅ **Excel and JSON** input test suite formats
- ✅ **Dynamic payloads** from external `.json` / `.xml` files
- ✅ **Environment variable injection** via `.env` (e.g. `{{AUTH_TOKEN}}`)
- ✅ **Consolidated Excel report** with conditional formatting
- ✅ **Standalone Windows EXE** via PyInstaller

---

## 📁 Project Structure

```
RestSoapApi/
├── src/                        # Core framework source code
│   ├── main.py                 # CLI entry point
│   ├── file_detector.py        # Detects REST vs SOAP from filename
│   ├── input_parser.py         # Parses JSON/Excel input files
│   ├── executor.py             # Runs test cases (serial / parallel)
│   ├── rest_client.py          # HTTP REST request handler
│   ├── soap_client.py          # SOAP request handler
│   ├── payload_loader.py       # Loads external JSON/XML payloads
│   ├── template_parser.py      # Resolves {{ENV_VAR}} placeholders
│   └── reporter.py             # Generates Excel report
│
├── data/
│   ├── input/                  # Test suite files (JSON preferred; xlsx auto-generated)
│   │   ├── TestSuite_REST.json
│   │   └── TestSuite_SOAP.json
│   ├── payloads/               # External payload files
│   │   ├── create_post.json
│   │   ├── update_post.json
│   │   ├── soap_add.xml
│   │   ├── soap_subtract.xml
│   │   └── soap_multiply.xml
│   └── output/                 # Generated reports (git-ignored)
│
├── generate_excel_inputs.py    # Converts JSON suites → styled Excel files
├── ApiAutomation.spec          # PyInstaller build spec
├── build.bat                   # One-click EXE build script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/RestSoapApi.git
cd RestSoapApi
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
copy .env.example .env
# Edit .env with your real API_BASE_URL, AUTH_TOKEN, SOAP_BASE_URL
```

### 4. (Optional) Generate Excel Input Files
```bash
python generate_excel_inputs.py
```

---

## ▶️ Usage

### Run REST test suite
```bash
python src/main.py data/input/TestSuite_REST.json
```

### Run SOAP test suite in parallel mode
```bash
python src/main.py data/input/TestSuite_SOAP.xlsx --parallel
```

### Run both suites together (consolidated report)
```bash
python src/main.py data/input/TestSuite_REST.json data/input/TestSuite_SOAP.json
```

Output report is saved to `data/output/report_<name>_<timestamp>.xlsx`.

---

## 🔨 Build Standalone EXE (Windows)

```bash
build.bat
```

The executable is generated at `dist/ApiAutomation.exe`.

```bash
dist\ApiAutomation.exe data\input\TestSuite_REST.json --parallel
```

---

## 📋 Input File Format

Test suite files must have `_REST` or `_SOAP` in their filename.

| Column | Description |
|--------|-------------|
| `TestCaseID` | Unique identifier |
| `Description` | Test description |
| `Method` | HTTP method (GET, POST, PUT, DELETE) |
| `Endpoint` | Full URL or path (supports `{{API_BASE_URL}}`) |
| `Headers` | JSON string of headers (supports `{{AUTH_TOKEN}}`) |
| `Payload` | Inline JSON payload or filename from `data/payloads/` |
| `SOAPAction` | SOAP action header (SOAP only) |
| `ExpectedStatus` | Expected HTTP status code (e.g. `200`) |

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | Base URL for REST APIs |
| `AUTH_TOKEN` | Bearer token or API key |
| `SOAP_BASE_URL` | Base URL for SOAP services |

Use `{{VARIABLE_NAME}}` syntax in test cases to inject values.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | REST HTTP client |
| `aiohttp` | Async/parallel HTTP |
| `openpyxl` | Excel report generation |
| `pandas` | Excel input parsing |
| `python-dotenv` | `.env` file loading |
| `pyinstaller` | EXE packaging |

---

## 📄 License

MIT License — free to use and modify.
