from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="CorpFinAI",
    description=(
        "Corporate Finance Autopilot: An agentic pipeline that ingests, "
        "models, and advises on any public company."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from api.routes_analysis import router as analysis_router
from api.routes_data import router as data_router
from api.routes_export import router as export_router
from api.routes_agent import router as agent_router
from api.routes_stream import router as stream_router

app.include_router(analysis_router, prefix="/api", tags=["Analysis"])
app.include_router(data_router, prefix="/api", tags=["Data"])
app.include_router(export_router, prefix="/api", tags=["Export"])
app.include_router(agent_router, prefix="/api", tags=["Agent"])
app.include_router(stream_router, prefix="/api", tags=["Stream"])


@app.get("/health")
def health():
    return {"status": "healthy", "service": "corpfinai"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
