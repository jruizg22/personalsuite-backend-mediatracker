from fastapi import APIRouter

from media_tracker.api.v1.tools import ytdlp_controller

router: APIRouter = APIRouter(
    prefix="/tools",
)

router.include_router(ytdlp_controller.router)