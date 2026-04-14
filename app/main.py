from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api_router import api_router
from app.core.config import settings

from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

app = FastAPI(title="IDFLab API")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "API working 🚀"}