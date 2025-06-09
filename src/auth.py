import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST': 
        username = request.form['username'].strip() # <-- ADD THIS
        password = request.form['password'].strip() # <-- ADD THIS
        db_session = current_app.extensions['db_manager'].get_database_session()
        error = ""

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if not error:
            try:
                new_user = User(username=username, password=generate_password_hash(password))
                db_session.add(new_user)
                db_session.commit()

            except IntegrityError:
                db_session.rollback()
                error = f"User {username} is already registered."
            except Exception as e:
                db_session.rollback()
                error = f"An unexpected error occurred: {e}"

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'].strip() # <-- ADD THIS
        password = request.form['password'].strip() # <-- ADD THIS
        print(f'User {username} logging in with password {password}')
        
        db_session = current_app.extensions['db_manager'].get_database_session()
        user = db_session.query(User).filter_by(username=username).first()

        error = ""
        if user is None:
            error = 'Incorrect username.'
            print("User does not exist")
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
            print("Wrong password")

        if not error:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        print("User not logged in")
        g.user = None
    else:
        db_session = current_app.extensions['db_manager'].get_database_session()
        g.user = db_session.query(User).filter_by(id=user_id).first()


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print("Running login required decorator")
        if g.user is None:
            print('No user!')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view