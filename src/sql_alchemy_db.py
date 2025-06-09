from sqlalchemy import Engine, create_engine
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
    engine: Engine
    current_scoped_session: scoped_session

    def __init__(self, engine: Engine, scoped_session_factory: scoped_session):
        self.engine = engine
        self.current_scoped_session = scoped_session_factory

    @classmethod
    def create_from_app(cls: Type['SQLAlchemyDB'], app: Flask) -> 'SQLAlchemyDB':
        """
        Factory method to create and initialize SQLAlchemyDB instance.
        """

        database_path = os.path.join(os.path.dirname(app.root_path), 'blog.sqlite')
        database_url = f"sqlite:///{database_path}"

        engine_instance = create_engine(
            database_url,
            echo=False,
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_instance)
        current_scoped_session = scoped_session(SessionLocal)

        # Create the SQLAlchemyDB instance with pre-initialized attributes
        db_instance = cls(engine_instance, current_scoped_session)

        # Register callbacks with the Flask app instance
        app.teardown_appcontext(db_instance.close_database_session)
       
    
        @click.command('init-db')
        @flask.cli.with_appcontext
        def build_tables_command():
            """Clear existing data and create new tables."""
            # Access the engine through the db_instance captured in the closure
            db_instance._run_build_tables()
            click.echo('Initialized the database tables.')
        app.cli.add_command(build_tables_command)

        return db_instance
    
    def get_database_session(self):
        """
        Returns the current SQLAlchemy session for the request.
        This session is managed by the connection pool and is unique to the current thread/request.
        """
        # Store the session in Flask's g object to be request-specific
        if 'db_session_instance' not in g:
            g.db_session_instance = self.current_scoped_session
        return g.db_session_instance

    def close_database_session(self, e=None):
        """
        Closes the current database session for the request and returns its connection
        to the pool. This function is registered as a Flask teardown callback.
        """
        db_session_to_close = g.pop('db_session_instance', None)
        if db_session_to_close is not None:
            db_session_to_close.close()
        # Crucial: Call remove() on the scoped_session to clean up the thread-local state
        # associated with the request, making it ready for the next request.
        self.current_scoped_session.remove()

    def _run_build_tables(self):
        """Internal method to execute table creation."""
        if self.engine is None:
             raise RuntimeError("Database engine not initialized. Call SQLAlchemyDB.create_from_app(app) first.")
        Base.metadata.create_all(bind=self.engine)