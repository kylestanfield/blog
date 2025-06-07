import datetime
import os
import sqlite3

from . import auth
from . import blog
from flask import Flask, request, jsonify, current_app

from .sql_alchemy_db import SQLAlchemyDB, Base

sqlite3.register_converter(
    "timestamp", lambda v: datetime.datetime.fromisoformat(v.decode())
)

def create_app(test_config=None):
    # create and configure flask app
    package_root = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(package_root, '..', 'templates')
    static_dir = os.path.join(package_root, '..', 'static')
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_mapping(
        SECRET_KEY='dev',
                SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'blog.sqlite')}",
                        SQLALCHEMY_TRACK_MODIFICATIONS=False
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

    app.extensions['db_manager'] = SQLAlchemyDB.create_from_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app