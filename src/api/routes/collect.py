from fastapi import APIRouter, BackgroundTasks, Request

from src.scheduler.jobs import collect_and_store_job

router = APIRouter(prefix="/api", tags=["collect"])


@router.post("/collect")
def trigger_collect(request: Request, background_tasks: BackgroundTasks) -> dict:
    settings = request.app.state.settings
    repository = request.app.state.repository
    background_tasks.add_task(collect_and_store_job, settings, repository)
    return {"status": "collect_started"}
