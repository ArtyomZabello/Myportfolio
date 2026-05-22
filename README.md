# Enterprise Test Automation Framework (Python / Playwright / Locust / DAST)

[![CI](https://github.com/ArtyomZabello/Myportfolio/actions/workflows/main.yml/badge.svg)](https://github.com/ArtyomZabello/Myportfolio/actions/workflows/main.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Allure Report](https://img.shields.io/badge/report-allure-orange.svg)](https://artyomzabello.github.io/Myportfolio/)

Production-grade test automation framework for the **Conduit (RealWorld)** application.  
Built as a multi-layer SDET platform covering functional, performance, security, and AI-assisted diagnostics.

## 📊 Live Test Reports (GitHub Pages)

| Report | Link |
|---|---|
| **Functional Tests (Allure)** | [https://artyomzabello.github.io/Myportfolio/](https://artyomzabello.github.io/Myportfolio/) |
| **Performance Tests (Locust)** | [https://artyomzabello.github.io/Myportfolio/locust_report.html](https://artyomzabello.github.io/Myportfolio/locust_report.html) |
| **Security Baseline Scan (ZAP)** | [https://artyomzabello.github.io/Myportfolio/zap_baseline_report.html](https://artyomzabello.github.io/Myportfolio/zap_baseline_report.html) |
| **Security API Scan (ZAP)** | [https://artyomzabello.github.io/Myportfolio/zap_api_report.html](https://artyomzabello.github.io/Myportfolio/zap_api_report.html) |

---

## Architecture

The framework follows a layered architecture with clear separation of concerns:

| Layer | Location | Responsibility |
|---|---|---|
| **Configuration** | `config/settings.py` | Centralized Pydantic settings from `.env` |
| **SUT** | `app/docker-compose.yml` | Containerized Conduit API + PostgreSQL |
| **API** | `src/api_client/` | httpx client, Pydantic DTOs, service layer |
| **Data Factory** | `src/data_factory/` | Faker-backed `UserDTO` / `ArticleDTO` builders |
| **UI (POM)** | `src/ui_pages/` | Playwright Page Objects + App facade |
| **Performance** | `performance/locustfile.py` | Locust `FastHttpUser` load scenarios |
| **Security (DAST)** | `security/` | OWASP ZAP baseline scan configuration |
| **AI RCA** | `src/ai_engine/` | Gemini 1.5 Flash fail-safe root cause analysis |

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Tests     │────▶│  Framework   │────▶│  Conduit SUT    │
│ API/UI/Load │     │ Layers + AI  │     │ :8000 / :4200   │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                    │
       ▼                    ▼
  Allure Report      OWASP ZAP DAST
  (GitHub Pages)     (baseline scan)
```

---

## Tech Stack

- **Python 3.12** — strict typing, Pydantic v2
- **pytest** + **pytest-playwright** + **pytest-xdist**
- **httpx** — synchronous API client
- **Playwright** — UI automation (headless in CI)
- **Locust** — performance / load testing
- **Faker** — synthetic test data
- **Allure** — rich test reporting
- **OWASP ZAP** — DAST security baseline
- **Google Gemini 1.5 Flash** — optional AI root cause analysis
- **Docker Compose** — reproducible SUT
- **GitHub Actions** — CI/CD pipeline
- **Ruff** + **Mypy** — linting and static type checking

---

## CI/CD Pipeline

The workflow is defined in [`.github/workflows/main.yml`](.github/workflows/main.yml):

1. **Linter & Type Check** — `ruff check` + `mypy`
2. **Test Execution Layer**
   - Start SUT via `docker compose`
   - Health check via `scripts/wait_for_backend.py`
   - API tests (`pytest tests/api/`)
   - UI tests headless (`pytest tests/ui/`)
   - Load smoke test (Locust, 30s)
   - OWASP ZAP baseline scan (Docker container, `--network host`)
3. **Reporting** — Allure report published to GitHub Pages (`gh-pages`)

### AI RCA in CI (Fail-Safe)

The AI layer **never fails the pipeline** when the API key is missing:

- `GeminiAnalyzer` returns `None` if `GEMINI_API_KEY` is empty or unset
- All HTTP / JSON errors are caught silently
- Failed tests still fail on their own assertions — AI only adds an Allure attachment

#### Enable AI RCA in GitHub Actions

1. Open **Repository Settings → Secrets and variables → Actions**
2. Create a new secret: `GEMINI_API_KEY`
3. Paste your Google Gemini API key
4. Re-run the workflow — failed tests will include **🤖 AI Root Cause Analysis** in Allure

> If the secret is not configured, tests run normally without AI attachments.

---

## Reporting

After a successful push to `main`, the Allure report is published at:

**https://artyomzabello.github.io/Myportfolio/**

The report includes:

- API request/response steps
- UI interaction traces
- Load test artifacts (when attached)
- AI RCA summaries (when `GEMINI_API_KEY` is configured)

Enable GitHub Pages: **Settings → Pages → Source: Deploy from branch `gh-pages`**.

---

## How to Run Locally

### Prerequisites

- Python 3.12+
- Docker Desktop (recommended for full SUT)
- Git

### Quick Start

```bash
# Clone and install
git clone https://github.com/ArtyomZabello/Myportfolio.git
cd Myportfolio
pip install -e ".[dev]"
playwright install chromium

# Bootstrap environment
cp .env.example .env

# Full API pipeline (Docker or mock fallback)
python scripts/run_all.py
```

### Makefile (Linux / Git Bash / WSL)

```bash
make env                  # create .env from .env.example
make up                   # start SUT (docker compose)
make wait-for-backend     # poll /api/tags until ready
make test-api             # run API tests
make test-load            # Locust headless load test
make test-security        # OWASP ZAP baseline scan
make run-all              # env → up → wait → test-api → down
```

### Windows (PowerShell)

```powershell
pip install -e ".[dev]"
playwright install chromium
python scripts/run_all.py          # API tests with auto mock fallback
python scripts/wait_for_backend.py # health check only
pytest tests/ -v --alluredir=allure-results
```

### UI Tests (requires frontend on :4200)

```bash
# Option A: mock UI for local/CI parity
python scripts/mock_conduit_ui_server.py &

# Option B: run your Conduit frontend on http://localhost:4200
pytest tests/ui/ -v --alluredir=allure-results
```

### View Allure Report Locally

```bash
allure serve allure-results
```

---

## Project Structure

```
Myportfolio/
├── .github/workflows/main.yml   # CI/CD pipeline
├── app/                         # Docker Compose SUT
├── config/                      # Pydantic settings
├── src/
│   ├── api_client/              # API layer
│   ├── data_factory/            # Test data builders
│   ├── ui_pages/                # Playwright POM
│   └── ai_engine/               # Gemini RCA
├── tests/
│   ├── api/
│   ├── ui/
│   └── unit/
├── performance/                 # Locust scenarios
├── security/                    # ZAP configuration
├── scripts/                     # Cross-platform runners
├── Makefile
└── pyproject.toml
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BASE_URL` | `http://localhost:8000/api` | Conduit API base URL |
| `UI_BASE_URL` | `http://localhost:4200` | Conduit frontend URL |
| `API_TIMEOUT` | `10.0` | HTTP timeout (seconds) |
| `GEMINI_API_KEY` | *(empty)* | Optional Gemini key for AI RCA |

Copy [`.env.example`](.env.example) to `.env` and adjust as needed.

---

## License

Portfolio project — Conduit (RealWorld) test automation framework.
