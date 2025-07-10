from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required
import re
from base64 import b64encode, b64decode

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

@bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q','').strip()
    if not query:
        return render_template('enter_search.html', query=query, results={})
    
    db=get_db()
    results = {
        'users':db.execute(
            '''
            SELECT * FROM user 
            WHERE username LIKE ? OR fullname LIKE ? OR instagram_id LIKE ? OR linkedin_id LIKE ? OR email LIKE ? OR about LIKE ?
            ''',
            (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')
        ).fetchall(),

        'blogs': db.execute(
            '''
            SELECT * FROM posts
            WHERE created LIKE ? OR title LIKE ? OR body LIKE?
            ''',
            (f'%{query}%', f'%{query}%', f'%{query}%')
        ).fetchall(),

        'comments': db.execute(
            '''
            SELECT * FROM comments
            WHERE body LIKE ?
            ''',
            (f'%{query}%',)
        ).fetchall(),
    }
    db.close()

    return render_template('search.html', query=query, results=results)

@bp.route('/<int:id>/profile', methods=('GET', 'POST'))
@login_required
def profile(id):
    db=get_db()

    user = db.execute(
        'SELECT * FROM user WHERE id=?', (id,)
    ).fetchone()
    blogs = db.execute(
        'SELECT * FROM posts WHERE author_id=?', (id,)
    ).fetchall()
    decoded_content=[]
    for blog in blogs:
        decoded_content.append(b64decode(blog['body'].encode()).decode())

    print(dict(user))
    return render_template('blog/profile.html', user=user, blogs=blogs, blog_bodies=decoded_content)


@bp.route('/<int:id>/post', methods=('GET','POST'))
@login_required
def post(id):
    db=get_db()
    query = request.args.get('query','')
    if request.method == 'POST':
        comment(id)

    post = db.execute(
        'SELECT * FROM posts WHERE id=?', (id,)
    ).fetchone()
    decoded_content = b64decode(post['body'].encode()).decode('utf-8')
    author = db.execute(
        'SELECT * FROM user WHERE id=?', (post['author_id'],)
    ).fetchone()
    comments=db.execute(
        'SELECT * FROM comments WHERE post_id=?', (id,)
    ).fetchall()
    if query:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted_post = pattern.sub(lambda m: f'<mark style="background-color: pink; padding: 2px 4px;">{m.group(0)}</mark>', decoded_content)
    else:
        highlighted_post = decoded_content
    m={}
    for comment in comments:
        user = db.execute(
            'SELECT * FROM user WHERE id=?', (comment['user_id'],)
        ).fetchone()
        m[comment['id']] = user['username']
    return render_template('blog/post.html', post=post, comments=comments, author=author, m=m, highlighted_post=highlighted_post )

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
    post = get_post(id)
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
        
    return render_template('blog/update.html', post=post, blogs=post, posts=post)

@bp.route('/<int:id>/update_comment', methods=('GET', 'POST'))
@login_required
def update_comment(id):
    db=get_db()
    comment = db.execute(
        'SELECT * FROM comments WHERE id=?', (id,)
    ).fetchone()
    if request.method=='POST':
        body = request.form['body']
        db.execute(
            'UPDATE comments SET body=? WHERE id=?', (body, comment['id'])
        )
        db.commit()
        return redirect(url_for('blog.post', id=comment['post_id']))
    
    return render_template('blog/update_comment.html', comment=comment)

@bp.route('/<int:id>/delete_comment', methods=('POST',))
@login_required
def delete_comment(id):
    db = get_db()
    comment= db.execute(
        'SELECT * FROM comments WHERE id=?', (id,)
    ).fetchone()
    db.execute(
        'DELETE FROM comments WHERE id=?', (id,)
    )
    db.commit()
    return redirect(url_for('blog.post', id=comment['post_id']))

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

