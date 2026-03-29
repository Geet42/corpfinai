# CorpFinAI: Corporate Finance Autopilot

An agentic corporate finance analysis pipeline that ingests public company data, builds deterministic financial models, runs AI-powered strategic advisory, and generates investor-grade outputs -- all with observable reasoning traces.

Built for the **Assiduous Hackathon 2025** (March 27-29).

> **Disclaimer:** This is a student hackathon project. All outputs are for educational purposes only and do not constitute investment advice. Projections are estimates based on publicly available data and stated assumptions.

---

## Quick Start

### Option A: Docker (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/Geet42/corpfinai.git
cd corpfinai

# 2. Set your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run everything
docker compose up --build

# 4. Open http://localhost:3000
```

### Option B: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env   # Edit with your API key
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Architecture

CorpFinAI is a pipeline-driven system with eight stages, each producing typed, validated outputs:

**1. Multi-Source Data Ingestion:** The system pulls company data from three sources: Yahoo Finance (via `yfinance`) for financial statements, price history, and company metadata; SEC EDGAR for 10-K filing text; and company websites for brand positioning text. Each source has independent error handling so a single source failure does not block the pipeline.

**2. Structured Storage:** All ingested data flows through Pydantic models for type validation and serialization, then persists to SQLite via SQLAlchemy. The database serves as the single source of truth that downstream components (financial engine, agent, generators) all query against. This separation means you can re-run analysis without re-ingesting data.

**3. RAG Indexing:** SEC 10-K filing text is cleaned, chunked using `RecursiveCharacterTextSplitter`, and indexed into a ChromaDB vector store. This enables the AI agent to perform retrieval-augmented queries over actual filing content for risk factors, competitive positioning, management outlook, and business segment details.

**4. Deterministic Financial Engine:** This is the critical architectural decision. All financial math (ratio analysis, 5-year projections, DCF valuation, sensitivity matrices, comparable multiples) runs as pure Python computation with no LLM involvement. The formulas are transparent, reproducible, and auditable. Revenue projections use compound growth, DCF uses Gordon Growth Model for terminal value, and sensitivity analysis sweeps across WACC and terminal growth rate combinations. The LLM decides *which assumptions* to feed in, but never computes numbers itself.

**5. Monte Carlo Simulation:** Beyond the three deterministic scenarios, the system runs 1,000 simulations with randomized assumptions (growth, margins, WACC, terminal growth) drawn from normal distributions anchored to historical data. The result is a full probability distribution of implied share prices with percentile breakdowns and a histogram visualization.

**6. LangChain ReAct Agent with RAG:** A GPT-4o-mini agent with tool-calling orchestrates the analysis. It has access to six tools: database retrieval, financial statement lookup, scenario projection (delegating to the deterministic engine), sensitivity analysis, chart data retrieval, and **RAG search over 10-K filings**. Every reasoning step (Thought, Action, Observation) is captured and returned in the API response. The frontend renders these as a collapsible trace viewer, satisfying the "observable steps, not one opaque prompt" judging criterion.

**7. Output Generation:** The pipeline produces an interactive React dashboard with Recharts visualizations, a downloadable **PPTX presentation** (via `python-pptx`) with company overview, financial tables, scenario comparison, and strategic advisory slides, and a **PDF investment memo** (via ReportLab) containing executive summary, financial highlights, scenario analysis, Monte Carlo summary, strategic advisory, and disclaimer.

**8. Quality Evaluation:** An automated evaluation engine runs 15+ sanity checks on every pipeline output: data completeness, ratio bounds (margins within [-100%, 100%]), DCF model validity, scenario ordering (Upside > Base > Downside), sensitivity matrix coverage, agent execution depth, RAG index coverage, and cross-validation of DCF against market cap. Results are displayed as pass/fail in the UI.

**SSE Live Streaming:** The entire pipeline streams progress via Server-Sent Events. The frontend updates in real-time as each stage completes (Ingestion, Storage, RAG Indexing, Financial Analysis, Monte Carlo, AI Agent, Output Generation, Quality Checks), providing a CI/CD-like experience.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Financial math separated from LLM | Deterministic computations are auditable and reproducible. LLM hallucination cannot corrupt the numbers. |
| ReAct agent over simple chain | Provides observable tool-calling traces. Each step is logged. Judges can see the AI "thinking." |
| RAG over 10-K filings | Enables qualitative analysis (risks, strategy) grounded in actual SEC documents, not LLM hallucinations. |
| Monte Carlo simulation | Provides probabilistic valuation range instead of just 3 point estimates. More realistic. |
| SSE over polling | Real-time pipeline progress without repeated API calls. Professional UX. |
| Quality evaluation layer | Automated sanity checks catch data issues and model anomalies. Shows production mindset. |
| Pydantic models everywhere | Type validation at every boundary. Automatic serialization. Production-grade data contracts. |
| SQLite over PostgreSQL | Zero-config setup. One `docker compose up` and it works. Appropriate for hackathon scope. |
| GPT-4o-mini over GPT-4 | Cost and speed optimized for hackathon. The deterministic engine handles the heavy lifting. |
| Three-scenario framework | Base/Upside/Downside is standard investment banking practice. Uses historical averages as anchors. |

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.0 | Backend API framework |
| Pydantic | 2.9.0 | Data validation and serialization |
| SQLAlchemy | 2.0.35 | Database ORM |
| yfinance | 0.2.43 | Yahoo Finance data ingestion |
| LangChain | 0.3.0 | ReAct agent orchestration |
| langchain-openai | 0.2.0 | OpenAI GPT-4o-mini integration |
| langchain-text-splitters | 0.3.0 | 10-K filing chunking for RAG |
| ChromaDB | 0.5.0 | Vector store for 10-K RAG retrieval |
| python-pptx | 1.0.2 | PPTX presentation generation |
| ReportLab | 4.2.0 | PDF investment memo generation |
| BeautifulSoup4 | 4.12.3 | Web scraping |
| NumPy | 2.1.0 | Monte Carlo simulation engine |
| Pandas | 2.2.3 | Financial data processing |
| React | 18.3 | Frontend framework |
| Recharts | 2.12 | Charts and data visualization |
| Tailwind CSS | 3.4 | UI styling |
| Docker | - | Containerized deployment |
| GitHub Actions | - | CI/CD pipeline (14 tests) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze/{ticker}` | Full pipeline: ingest, model, analyze, generate |
| GET | `/api/analyze/{ticker}/stream` | SSE stream: real-time pipeline progress |
| GET | `/api/company/{ticker}` | Retrieve stored company profile |
| GET | `/api/company/{ticker}/financials` | Retrieve stored financial statements |
| POST | `/api/agent/query` | Freeform agent query with traces |
| GET | `/api/export/{ticker}/pptx` | Download generated PPTX presentation |
| GET | `/api/export/{ticker}/pdf` | Download generated PDF investment memo |
| GET | `/health` | Health check |

---

## Limitations

- **Data quality:** yfinance data can have gaps or inconsistencies for some tickers. The system handles missing fields gracefully with defaults.
- **LLM hallucination risk:** Mitigated by the deterministic math layer. The agent reasons about assumptions but never invents financial figures.
- **No real-time data:** Financial statements are annual. Price history is historical, not streaming.
- **Simplified projections:** FCF = EBITDA - Capex (ignores tax and working capital adjustments for hackathon scope).
- **SEC EDGAR:** Basic text extraction from 10-K filings. Section-level NLP parsing not yet implemented.
- **Single company:** Analyzes one company at a time. No comparison mode yet.

---

## Third-Party APIs and Data Sources

| Source | Type | Notes |
|--------|------|-------|
| Yahoo Finance (yfinance) | Financial data | Open-source library, no API key needed |
| SEC EDGAR | Filing text | Public API, requires User-Agent header |
| Company websites | Brand info | Respectful scraping with identified User-Agent |
| OpenAI GPT-4o-mini | AI reasoning | Requires API key. System works without it (agent disabled, deterministic model still runs) |

---

## What I'd Do With Another Week

- **LBO and merger models:** Add leveraged buyout and M&A merger model capabilities to the financial engine.
- **Multi-company comparison:** Side-by-side analysis of peer companies with relative valuation.
- **Real-time data feeds:** WebSocket integration for live price updates.
- **Authentication and deploy:** User accounts, saved analyses, deploy to cloud (Railway/Fly.io).
- **More sophisticated valuation:** Working capital projections, tax modeling, debt schedule modeling.
- **Deeper 10-K parsing:** NLP-based section extraction (Item 1, Item 1A, Item 7) for more targeted RAG retrieval.
- **Excel export:** Generate editable .xlsx financial models alongside PPTX and PDF.

---

## AI Tools Used During Development

- **GPT-4o-mini** via LangChain for agentic financial reasoning within the application
- **Claude** for architecture design, code scaffolding, and debugging
- **GitHub Copilot** for boilerplate acceleration

---

## Project Structure

```
corpfinai/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .github/workflows/ci.yml
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Pydantic settings
│   ├── requirements.txt
│   ├── models/                    # Pydantic data models
│   ├── ingestion/                 # Data sources (yfinance, SEC, web)
│   ├── database/                  # SQLite + SQLAlchemy
│   ├── financial_engine/          # Deterministic math (ratios, DCF, sensitivity, Monte Carlo)
│   ├── agent/                     # LangChain ReAct agent + tools + RAG engine
│   ├── evaluation/                # Automated quality checks (15+ sanity checks)
│   ├── generators/                # PPTX, PDF memo, advisory output
│   ├── api/                       # FastAPI routes (REST + SSE streaming)
│   └── tests/                     # 14 unit tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/            # 11 React components
│   │   ├── hooks/useAnalysis.js   # SSE-powered analysis hook
│   │   └── utils/api.js
│   └── package.json
├── README.md
└── WRITEUP.md
```

---

## License

MIT License. Built for the Assiduous Hackathon 2025.
