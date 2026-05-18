from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(prefix="/api", tags=["news"])


def _rows_to_list(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(r) if not isinstance(r, dict) else r for r in rows]


@router.get("/news")
def list_news(
    request: Request,
    days: int = Query(default=1, ge=1, le=30),
    limit: int = Query(default=50, ge=1, le=500),
) -> dict:
    repo = request.app.state.repository
    if repo is None:
        raise HTTPException(status_code=500, detail="Repository not initialized")

    rows = repo.get_news_last_hours(days * 24)
    items = _rows_to_list(rows)[:limit]

    return {"total": len(items), "news": items}
