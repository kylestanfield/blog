from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask import g, Flask # current_app is implicitly used via 'app' argument
import flask.cli
import click
import os
from typing import Type # For type hinting classmethods

# Base class for your SQLAlchemy models
Base = declarative_base()

class SQLAlchemyDB:
    """
    Class to manage the SQLAlchemy engine, session,
    and integrate with Flask.
    """
    engine: create_engine
    scoped_session: scoped_session # type: ignore

    def __init__(self, engine: create_engine, scoped_session_factory: scoped_session): # type: ignore
        self.engine = engine
        self.scoped_session = scoped_session_factory

    @classmethod
    def create_from_app(cls: Type['SQLAlchemyDB'], app: Flask) -> 'SQLAlchemyDB':
        """
        Factory method to create and initialize SQLAlchemyDB instance.
        """

        instance_path = app.instance_path
        os.makedirs(instance_path, exist_ok=True)

        database_path = os.path.join(instance_path, 'blog.db')
        database_url = f"sqlite:///{database_path}"

        engine_instance = create_engine(
            database_url,
            echo=False,  # Set to True to log SQL statements (useful for debugging)
            connect_args={"check_same_thread": False}, # Essential for SQLite with multiple threads
            # Pooling options for fine-tuning (defaults are often sufficient for SQLite)
            # pool_size=10,
            # max_overflow=5,
            # pool_recycle=3600 # Recycle connections after 1 hour to avoid stale ones
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_instance)
        scoped_session_instance = scoped_session(SessionLocal)

        # Create the SQLAlchemyDB instance with pre-initialized attributes
        db_instance = cls(engine_instance, scoped_session_instance)

        # Register callbacks with the Flask app instance
        app.teardown_appcontext(db_instance.close_db)
       
       
        # Optional: Define a simple CLI command to create tables
        # You'd typically use a migration tool like Alembic for production
        @click.command('build-tables')
        @flask.cli.with_appcontext
        def build_tables_command():
            """Clear existing data and create new tables."""
            # Access the engine through the db_instance captured in the closure
            db_instance._run_build_tables()
            click.echo('Initialized the database tables.')
        app.cli.add_command(build_tables_command)

        return db_instance
    
    def get_db(self):
        """
        Returns the current SQLAlchemy session for the request.
        This session is managed by the connection pool and is unique to the current thread/request.
        """
        # Store the session in Flask's g object to be request-specific
        if 'db_session_instance' not in g:
            g.db_session_instance = self.scoped_session()
        return g.db_session_instance

    def close_db(self, e=None):
        """
        Closes the current database session for the request and returns its connection
        to the pool. This function is registered as a Flask teardown callback.
        """
        db_session_to_close = g.pop('db_session_instance', None)
        if db_session_to_close is not None:
            db_session_to_close.close()
        # Crucial: Call remove() on the scoped_session to clean up the thread-local state
        # associated with the request, making it ready for the next request.
        self.scoped_session.remove()

    def _run_build_tables(self):
        """Internal method to execute table creation."""
        if self.engine is None:
             raise RuntimeError("Database engine not initialized. Call SQLAlchemyDB.create_from_app(app) first.")
        Base.metadata.create_all(bind=self.engine)