from typing import Generator, Any, Callable

from fastapi import APIRouter, FastAPI
from sqlalchemy import Engine
from sqlmodel import Session

class Module:
    """
    Represents a generic module for the application.

    This class provides a structure to initialize a module with the
    FastAPI application and SQLAlchemy/SQLModel engine, create session
    providers, and register API routes with the application.

    Attributes:
        app (FastAPI): The main FastAPI application instance.
        engine (Engine): The SQLAlchemy/SQLModel engine used for database sessions.
    """

    def __init__(self, app: FastAPI, engine: Engine) -> None:
        """
        Initializes the Module with the application and engine.

        Args:
            app (FastAPI): The main FastAPI application instance.
            engine (Engine): The database engine used to create sessions.
        """
        self.app: FastAPI = app
        self.engine: Engine = engine

    def get_session(self) -> Callable[[], Generator[Session, Any, None]]:
        """
        Creates a session provider function for database access.

        Returns:
            Callable[[], Generator[Session, None, None]]:
                A function that yields a SQLModel Session when called,
                suitable for use as a FastAPI dependency.

        Example:
            session_provider = module.get_session()
            with session_provider() as session:
                # use the session
        """
        def _get_session():
            with Session(self.engine) as session:
                yield session

        return _get_session

    def register(self) -> None:
        """
        Registers the module's API routes with the FastAPI application.

        This method:
            - Imports the module's API endpoints.
            - Creates an APIRouter with a module-specific prefix and tags.
            - Includes sub-routers for specific features (e.g., YouTube channels).
            - Attaches the module router to the main FastAPI app.

        It should be called after the module is initialized.
        """
        from .api.v1 import yt_channel_endpoints

        # Create the main router for this module
        module_router: APIRouter = APIRouter(prefix="/media_tracker", tags=["media_tracker"])

        # Include the endpoints as sub-routers
        module_router.include_router(
            yt_channel_endpoints.get_router(self.get_session()),
            prefix="/yt_channels",
            tags=["yt_channels"]
        )

        # Attach the module router to the main FastAPI app
        self.app.include_router(module_router)