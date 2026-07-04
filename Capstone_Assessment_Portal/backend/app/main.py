from fastapi import FastAPI

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.category_routes import router as category_router
from app.api.v1.question_routes import router as question_router
from app.config.database import ensure_indexes
from app.exceptions.exception_handlers import register_exception_handlers

app = FastAPI(
    title="Assessment Portal API",
    description="Backend APIs for the Assessment Portal capstone project",
    version="1.0.0",
)

register_exception_handlers(app)


@app.on_event("startup")
async def on_startup():
    """
    Run application startup tasks.
    """
    await ensure_indexes()


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(question_router)


@app.get("/")
def health_check():
    """
    Check if the Assessment Portal API is running.
    """
    return {"message": "Assessment Portal API is running"}