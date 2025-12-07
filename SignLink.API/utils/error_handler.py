from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
import os

# -------------------------------------------------------------------
# Step 1: Set up a logger for backend error tracking
# -------------------------------------------------------------------

logger = logging.getLogger("app.errors")
logger.setLevel(logging.ERROR)

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# File handler for persistent logging
file_handler = logging.FileHandler(os.path.join(log_dir, "error.log"))
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# -------------------------------------------------------------------
# Step 2: Register global exception handlers
# -------------------------------------------------------------------

def register_exception_handlers(app):
    """Register global exception handlers for consistent API responses."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handles standard HTTP errors like 404, 403, etc."""
        logger.error(f"HTTPException: {exc.detail} | Path: {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail or "An unexpected error occurred.",
                "context": "http"
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handles validation issues (missing fields, wrong data type, etc.)."""
        logger.error(f"ValidationError: {exc.errors()} | Path: {request.url}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Invalid request format or missing required fields.",
                "context": "validation"
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handles DB connection errors or failed queries."""
        logger.error(f"SQLAlchemyError: {str(exc)} | Path: {request.url}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database error. Please try again later.",
                "context": "database"
            },
        )

    @app.exception_handler(ConnectionError)
    async def connection_error_handler(request: Request, exc: ConnectionError):
        """Handles API/Backend downtime scenarios (US9-03)."""
        logger.error(f"ConnectionError: {str(exc)} | Path: {request.url}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Server unavailable. Please try again later.",
                "context": "network"
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch-all for unexpected server errors (US9-06, US9-07)."""

        # Log both the short message and full traceback
        error_message = f"Exception occurred: {exc} | Path: {request.url}"
        logger.error(error_message)
        logger.error(traceback.format_exc())

        # Also emit to root logger so pytest caplog can intercept
        import logging
        logging.getLogger().error(error_message)
        logging.getLogger().error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": "Unexpected server error. Please try again later.",
                "context": "generic"
            },
        )