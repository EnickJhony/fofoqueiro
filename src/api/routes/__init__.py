from fastapi import APIRouter

from src.api.routes.collect import router as collect_router
from src.api.routes.health import router as health_router
from src.api.routes.news import router as news_router
from src.api.routes.summaries import router as summaries_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(news_router)
api_router.include_router(summaries_router)
api_router.include_router(collect_router)
