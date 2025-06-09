from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from sqlalchemy.orm import joinedload

from .auth import login_required
from .models import Post

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db_session = current_app.extensions['db_manager'].get_database_session()
    posts = db_session.query(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc()).all()

    # Fetch a few recent posts for the "Other Posts" section
    recent_posts = db_session.query(Post).order_by(Post.created_at.desc()).limit(5).all()
    return render_template('blog/index.html', posts=posts, recent_posts=recent_posts)

# Route to view a single post
@bp.route('/<int:id>/')
def view(id):
    db_session = current_app.extensions['db_manager'].get_database_session()
    post = db_session.query(Post).options(joinedload(Post.author)).filter(Post.id == id).first()
    
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # Fetch a few recent posts for the "Other Posts" section
    recent_posts = db_session.query(Post).order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('blog/view.html', post=post, recent_posts=recent_posts)

# Route to create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print("Create")
    if request.method == "POST":
        db_session = current_app.extensions['db_manager'].get_database_session()
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            new_post = Post(author_id=g.user.id, title=title, body=body)
            db_session.add(new_post)
            db_session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# Function to get a post and check ownership
def get_post(id, check_author=True):
    db_session = current_app.extensions['db_manager'].get_database_session()
    post = db_session.query(Post).options(joinedload(Post.author)).filter(Post.id == id).first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403) # Forbidden

    return post

# Route to update a post
@bp.route('/<int:id>/update/', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    db_session = current_app.extensions['db_manager'].get_database_session()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db_session.commit()
            return redirect(url_for('blog.view', id=post.id))

    return render_template('blog/update.html', post=post)

# Route to delete a post
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id) # Checks for existence and ownership
    db_session = current_app.extensions['db_manager'].get_database_session()
    post_to_delete = db_session.query(Post).filter(Post.id == id).first()
    db_session.delete(post_to_delete)
    db_session.commit()
    return redirect(url_for('blog.index'))