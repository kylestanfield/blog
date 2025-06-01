from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from .auth import login_required
from .models import Post

bp = Blueprint('blog', __name__)

# a simple page that says hello
@bp.route('/')
def index():
    db_session = current_app.extensions['db_manager'].get_database_session()
    posts = db_session.query(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc()).all()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == "POST":
        db_session = current_app.extensions['db_manager'].get_database_session()
    
        error = ""
        post_title = request.form['title']
        post_body = request.form['body']
        if not post_title:
            error = "You must enter a title."
        elif not post_body:
            error = "You must enter a body for your post."
        if not error:
            try:
                new_post = Post(author_id=g.user.id, title=post_title, body=post_body)
                db_session.add(new_post)
                db_session.commit()
                return redirect(url_for('index'))
            except IntegrityError:
                db_session.rollback()
                error = "Integrity error when creating post"
            except Exception as e:
                db_session.rollback()
                error = f"An unexpected error occurred: {e}"
        flash(error)
    return render_template('/blog/create.html')

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.method == 'POST':
        pass
    return render_template('/blog/update.html')