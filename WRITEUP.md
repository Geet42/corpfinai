# CorpFinAI: One-Page Write-Up

## Problem

Investment professionals spend hours manually collecting company data across scattered sources, building financial models in spreadsheets, and assembling presentations. Existing tools are either prohibitively expensive (Bloomberg terminals) or too shallow (basic stock screeners) to produce actionable analysis. There is no accessible, pipeline-driven tool that automates the full workflow from data ingestion to investor-grade output with transparent reasoning.

## Approach

CorpFinAI is an eight-stage pipeline system:

**1. Multi-source ingestion** pulls financial statements from Yahoo Finance, 10-K filing text from SEC EDGAR, and brand positioning from company websites into typed Pydantic models stored in SQLite.

**2. A deterministic financial engine** computes historical ratio analysis, three-scenario (Base/Upside/Downside) revenue and FCF projections, DCF valuation via Gordon Growth Model, WACC vs terminal growth sensitivity matrices, and comparable company multiples. All math is pure Python with no LLM involvement, ensuring reproducibility and auditability.

**3. A LangChain ReAct agent** (GPT-4o-mini) orchestrates the analysis through tool-calling. It retrieves data from the database, runs scenario projections by delegating to the deterministic engine, and synthesizes findings. Every Thought/Action/Observation step is captured and returned for observability.

**4. RAG engine** indexes 10-K filing text using ChromaDB vector store and RecursiveCharacterTextSplitter, enabling the agent to query risk factors, strategy, and competitive positioning through semantic search.

**5. Monte Carlo simulation** runs 1000 probabilistic scenarios with randomized growth, margins, and WACC parameters, generating distributions with percentiles and confidence intervals for robust valuation ranges.

**6. Output generators** produce an interactive React dashboard (Recharts visualizations, real-time SSE streaming, agent trace viewer) and downloadable PPTX/PDF corporate presentations.

**7. Quality evaluation engine** runs 15+ automated sanity checks on data completeness, financial ratio bounds, scenario consistency, and cross-validation between DCF and market valuations.

**8. Docker + CI** enables one-command startup (`docker compose up`) and automated testing/linting via GitHub Actions with multi-stage builds.

## Trade-Offs

- Used **SQLite over Postgres** for zero-config hackathon setup.
- Used **GPT-4o-mini over GPT-4** for cost and speed; the deterministic engine carries the analytical weight.
- **Simplified FCF** (EBITDA minus Capex) skips tax and working capital modeling for scope.
- RAG indexing extracts sections via regex patterns (business, risks, strategy) rather than advanced NLP parsing.
- System **works without an OpenAI key**: the deterministic model, charts, PPTX, and full dashboard run independently; only the agent reasoning layer requires it.

## What I'd Do Next

With another week: add LBO and merger model capabilities, build multi-company comparison mode, deploy to cloud with authentication, implement advanced NLP section parsing for 10-K filings, and add options pricing models.

## AI Tools Used

- **GPT-4o-mini** via LangChain: agentic financial reasoning within the application (tool-calling, scenario selection, advisory generation)
- **Claude**: architecture design, code scaffolding, implementation guidance
- **GitHub Copilot**: boilerplate acceleration

## Key Prompts Used

The agent system prompt enforces a structured workflow (retrieve data, analyze trends, build scenarios, run sensitivity, synthesize) and critical rules: always use the calculator tool for projections, never fabricate numbers, cite data points, label outputs as estimates. The ReAct format (Thought/Action/Observation) ensures every reasoning step is visible and logged.

The advisory generator prompt gives the LLM structured financial metrics and scenario results, then asks for funding options, strategic options, capital allocation recommendations, and risk factors while enforcing disclaimer labeling.
