"""
Application entry point for the Assessment Portal API.

Registers routers and global exception handlers that map domain
exceptions raised in the service layer to proper HTTP responses.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.attempt_routes import router as attempt_router
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.category_routes import router as category_router
from app.api.v1.question_routes import router as question_router
from app.api.v1.quiz_routes import router as quiz_router
from app.api.v1.result_routes import router as result_router
from app.config.database import ensure_indexes
from app.exceptions.exception_handlers import register_exception_handlers

app = FastAPI(
    title="Assessment Portal API",
    description="Backend APIs for the Assessment Portal capstone project",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.on_event("startup")
async def on_startup():
    """
    Run initialization tasks when the application starts.
    """
    await ensure_indexes()


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(quiz_router)
app.include_router(question_router)
app.include_router(attempt_router)
app.include_router(result_router)


@app.get("/")
def health_check():
    """
    Check if the Assessment Portal API is running.
    """
    return {"message": "Assessment Portal API is running"}