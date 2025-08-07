from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/generate/v2/", include_in_schema=False)
def redirect_to_generate():
    return RedirectResponse(url="/generate/", status_code=301)
