import datetime
import os
import sqlite3

from . import auth
from flask import Flask, request, jsonify, current_app

from .sql_alchemy_db import SQLAlchemyDB

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def create_app(test_config=None):
    # create and configure flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # We are not testing, load the instance config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.db_manager = SQLAlchemyDB.create_from_app(app)

    app.register_blueprint(auth.bp)
    

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, world!'
    
    return app