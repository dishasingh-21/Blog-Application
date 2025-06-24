from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)
@bp.route('/')
def index():
    posts = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM posts p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    comments = get_db().execute(
        'SELECT * FROM comments ORDER BY reacted DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts, comments=comments)

@bp.route('/<int:id>/profile', methods=('GET', 'POST'))
@login_required
def profile(id):
    db=get_db()

    user = db.execute(
        'SELECT * FROM user WHERE id=?', (id,)
    ).fetchone()
    blogs = db.execute(
        'SELECT body FROM posts WHERE author_id=?', (id,)
    ).fetchall()

    return render_template('blog/profile.html', user=user, blogs=blogs)


@bp.route('/<int:id>/post', methods=('GET','POST'))
@login_required
def post(id):
    db=get_db()
    if request.method == 'POST':
        comment(id)

    post = db.execute(
        'SELECT * FROM posts WHERE id=?', (id,)
    ).fetchone()
    author = db.execute(
        'SELECT * FROM user WHERE id=?', (post['author_id'],)
    ).fetchone()
    comments=db.execute(
        'SELECT * FROM comments WHERE post_id=? ORDER BY reacted DESC', (id,)
    ).fetchall()

    return render_template('blog/post.html', post=post, comments=comments, author=author)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO posts (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM posts p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id=?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/comment', methods=('GET', 'POST'))
@login_required
def comment(id):
    db = get_db()
    post = db.execute(
        'SELECT * FROM posts WHERE id= ?', (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if request.method == 'POST':
        body = request.form['body']

        db.execute(
            'INSERT INTO comments(post_id, user_id, body)'
            ' VALUES (?, ?, ?)',
            (post['id'], g.user['id'], body)
        )
        db.commit()
        return redirect(url_for('blog.post', id=id))
    
    return render_template('blog/comment.html', post=post)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    posts = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE posts SET title = ?, body = ?'
                ' WHERE id=?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', posts=posts, blogs=posts)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

