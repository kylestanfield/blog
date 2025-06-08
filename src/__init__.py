import datetime
import os
import sqlite3
import sys

from . import auth
from . import blog
from .models import Post
from flask import Flask, current_app
from flask_frozen import Freezer
from sqlalchemy.orm import joinedload


from .sql_alchemy_db import SQLAlchemyDB, Base

sqlite3.register_converter(
    "timestamp", lambda v: datetime.datetime.fromisoformat(v.decode())
)

def blog_update_url_generator():
    # You need an application context to access current_app and db_manager
    with current_app.app_context():
        db_session = current_app.extensions['db_manager'].get_database_session()
        # Assuming you have a Post model in blog_models
        # Adjust 'Post' and 'post_id' if your model/column names are different
        posts = db_session.query(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc()).all()
        for post in posts:
            yield ('blog.view', {'id': post.id})


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
    app.add_url_rule('/', endpoint='index', view_func=blog.index)
    
    return app