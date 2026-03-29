from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile

router = APIRouter()


@router.get("/export/{ticker}/pptx")
async def export_pptx(ticker: str):
    """Download the generated PPTX presentation."""
    path = os.path.join(tempfile.gettempdir(), f"{ticker.upper()}_presentation.pptx")
    if not os.path.exists(path):
        raise HTTPException(
            404, "Presentation not generated yet. Run /analyze first."
        )
    return FileResponse(
        path,
        filename=f"{ticker.upper()}_CorpFinAI.pptx",
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".presentationml.presentation"
        ),
    )


@router.get("/export/{ticker}/pdf")
async def export_pdf(ticker: str):
    """Download the generated PDF investment memo."""
    path = os.path.join(tempfile.gettempdir(), f"{ticker.upper()}_memo.pdf")
    if not os.path.exists(path):
        raise HTTPException(
            404, "PDF memo not generated yet. Run /analyze first."
        )
    return FileResponse(
        path,
        filename=f"{ticker.upper()}_CorpFinAI_Memo.pdf",
        media_type="application/pdf",
    )
