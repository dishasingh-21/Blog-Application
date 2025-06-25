import functools
from flask import(
    Blueprint, flash, g, redirect, render_template,request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username,fullname, about, email, instagram_id, linkedin_id) VALUES (?,?,?,?,?,?)",
                    (username,None,None,None,None,None)
                )
                db.commit()
                id = db.execute(
                    "SELECT id FROM user WHERE username=?", (username,)
                ).fetchone()[0]
                db.execute(
                    "INSERT INTO pass (id, password) VALUES (?,?)", (id, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()
        
        Pass = db.execute(
            'SELECT password FROM pass WHERE id=?', (user['id'],)
        ).fetchone()[0]
        if user is None:
            error = 'Incorrect username!'
        elif not check_password_hash(Pass, password):
            error = 'Incorrect password!'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if has_entered_details(user['id']): return redirect(url_for('blog.index'))
            else: return redirect(url_for('auth.enter_details'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.route('/enter-details', methods=('GET','POST'))
def enter_details():
    if request.method == 'POST':
        fullname = request.form['fullname']
        about = request.form['about'] or None
        email = request.form['email'] or None
        instagram_id = request.form['instagram_id'] or None
        linkedin_id = request.form['linkedin_id'] or None
        user_id = g.user['id']
        db=get_db()
        db.execute(
            'UPDATE user SET fullname=?, about=?, email=?, instagram_id=?, linkedin_id=? WHERE id=?',
            (fullname, about, email, instagram_id, linkedin_id, user_id)
        )
        db.commit()
        return redirect(url_for('blog.profile', id=user_id))
    
    return render_template('auth/enter_details.html')

def has_entered_details(id):
    db=get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id=?', (id,)
    ).fetchone()

    return user and user['fullname']

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view





    
    