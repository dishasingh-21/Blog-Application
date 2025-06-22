import os

from flask import Flask, request, render_template
from . import db
from . import auth
from . import blog

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    @app.route('/hello')
    def hello():
        return '<h1> Hello, World! </h1> <h2> Hello hello </h2> '

    @app.route('/pumpkin')
    def pumpkin():
        return 'Halloween is not near hehehe'

    @app.route('/greeting',methods=['GET'])
    def greeting():
        args = request.args
        cute = args.get('name')
        return render_template('greeting.html', var = cute)

    @app.route('/sum',methods=['GET'])
    def sum():
        args = request.args
        a = int(args.get('a'))
        b = int(args.get('b'))
        return f'{a} + {b} =' + str(a+b)
    
    return app

if __name__ == '__main__':
    create_app()
