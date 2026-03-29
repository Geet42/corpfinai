from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import settings

router = APIRouter()


class AgentQuery(BaseModel):
    ticker: str
    question: str


@router.post("/agent/query")
async def agent_query(query: AgentQuery):
    """Freeform agent query with full reasoning traces."""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            400,
            "Agent requires OPENAI_API_KEY. Set it in .env file.",
        )

    from agent.orchestrator import CorpFinAgent

    agent = CorpFinAgent()
    result = agent.analyze(query.ticker.upper(), query.question)
    return result
