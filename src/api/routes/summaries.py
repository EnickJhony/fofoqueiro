from datetime import date

from fastapi import APIRouter, HTTPException, Request

from src.summarizer.daily_summary import build_daily_summary

router = APIRouter(prefix="/api", tags=["summaries"])


@router.get("/summaries/{date_str}")
def get_summary(request: Request, date_str: str) -> dict:
    repo = request.app.state.repository
    if repo is None:
        raise HTTPException(status_code=500, detail="Repository not initialized")

    try:
        day = date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc

    rows = repo.get_news_for_day(day)
    summary = build_daily_summary(rows, day)
    return {"date": day.isoformat(), "summary": summary}
