# app/core/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

# handling HTTP exceptions (404, 401)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
        },
    )

# validation error 422
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erro_msg = exc.errors()[0].get("msg")
    campo = exc.errors()[0].get("loc")[-1]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": f"Erro de validação no campo '{campo}': {erro_msg}",
        },
    )

# error 500 for unhandled exceptions
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, SQLAlchemyError):
        print(f"Erro no banco de dados: {str(exc)}")
    else:
        print(f"Erro crítico no servidor: {str(exc)}")
        
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ocorreu um erro interno no servidor. Tente novamente mais tarde.",
        },
    )