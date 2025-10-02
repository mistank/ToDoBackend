"""
Centralizovani exception handling za aplikaciju.
Omogućava konzistentan handling grešaka bez promene formata odgovora.
"""
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from typing import Optional
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def handle_database_error(e: Exception, operation: str = "Database operation", detail: Optional[str] = None):
    error_msg = str(e)

    logger.error(f"{operation} failed: {error_msg}", exc_info=True)

    # IntegrityError - unique constraint, foreign key violations
    if isinstance(e, IntegrityError):
        if "Duplicate entry" in error_msg or "UNIQUE constraint" in error_msg:
            if detail:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Record already exists"
            )
        elif "foreign key constraint" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference to related record"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database constraint violation"
            )

    # OperationalError - connection issues, table doesn't exist, etc
    if isinstance(e, OperationalError):
        logger.critical(f"Database operational error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable"
        )

    # Generic SQLAlchemy errors
    if isinstance(e, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

    # Unexpected errors
    logger.critical(f"Unexpected error in {operation}: {error_msg}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )


def handle_not_found(resource_name: str, resource_id: Optional[any] = None):
    detail = f"{resource_name} not found"
    if resource_id:
        detail += f" (id: {resource_id})"

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def handle_validation_error(detail: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def safe_commit(db, operation: str = "Commit operation"):
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        handle_database_error(e, operation)


def safe_db_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            # Već handleovano, samo prosleđujemo
            raise
        except Exception as e:
            # Handleuj neočekivane greške
            handle_database_error(e, func.__name__)

    return wrapper
