from flask import Flask, request, json, jsonify, abort, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from functools import wraps
from datetime import datetime

app = Flask(__name__)
config = json.load(open('config.json', 'r'))
app.config['SECRET_KEY'] = config['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = config['db_connection_string']
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
API_NAME = config['api_name']


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120))

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=9999):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
            print(data)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        user = User.query.get(data['id'])
        print(user)
        return user


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)
    tags = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


def AuthenticationRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(403, "1 You are forbidden to view this page.")
        user = User.verify_auth_token(token)
        if not user:
            abort(403, "2 You are forbidden to view this page.")
        g.user = user

        return f(*args, **kwargs)
    return decorated_function


@app.route('/api')
def v1index():
    return jsonify({
        "name": API_NAME,
        "status": "OK",
        "code": 200
    }), 200

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    if not username or not password:
        abort(400)
    if User.query.filter_by(username=username).first():
        abort(400)

    user = User(username=username, email=email, name=name)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    data = {
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "id": user.id
    }
    return jsonify(data), 201


@app.route('/api/login', methods=['POST'])
def verify_password():
    g.user = None
    if request.json.get('token'):
        user = User.verify_auth_token(request.json.get('token'))
        if not user:
            abort(401, "1Authorization token is invalid or expired")
        g.user = user
        data = {
            'id': g.user.id,
            'username': g.user.username,
            'name': g.user.name,
            'email': g.user.email,
            'token': g.user.generate_auth_token(9999)
        }
        print("token var")
        return jsonify(data), 200

    elif request.json.get('username') and request.json.get('password'):
        user = User.query.filter_by(
            username=request.json.get('username')).first()
        if not user:
            abort(401, "2Authorization token is invalid orexpired")
        is_password_valid = user.verify_password(request.json.get('password'))
        if not user or not is_password_valid:
            abort(401, "3Authorization token is invalid orexpired")
        g.user = user
        data = {
            'id': g.user.id,
            'username': g.user.username,
            'name': g.user.name,
            'email': g.user.email,
            'token': g.user.generate_auth_token(9999).decode('utf-8')
        }
        print("token yok")
        return jsonify(data), 200
    print("asdasd")
    abort(400)


@app.route('/api/users')
def get_users():
    users = User.query.all()
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email
        })
    return jsonify(users=data), 200


@app.route('/api/users/<int:id>')
def get_user(id):
    print(id)
    user = User.query.filter_by(id=id).first()
    if not user:
        abort(404)

    data = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'email': user.email
    }

    return jsonify(data), 200


@app.route('/api/users/<int:id>', methods=['DELETE'])
@AuthenticationRequired
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        abort(404)

    data = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'email': user.email
    }

    db.session.delete(user)
    db.session.commit()

    return jsonify(data), 200


@app.route('/api/users/<int:id>', methods=['PATCH'])
@AuthenticationRequired
def update_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        print("user", id)
        abort(404)

    if not request.json:
        print("json")
        abort(404)

    name = request.json.get('name')
    username = request.json.get('username')
    email = request.json.get('email')

    data = {}

    if username:
        check_user = User.query.filter_by(username=username).first()
        if check_user and check_user.id is not id:
            abort(400, "username is already in use")

        data['username'] = username
        user.username = username

    if email:
        data['email'] = email
        user.email = email

    if name:
        data['name'] = name
        user.name = name
    if not data:
        abort(400)

    db.session.commit()
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "User profile updated."
    }), 200


@app.route('/api/blogposts', methods=['POST'])
@AuthenticationRequired
def add_blogpost():

    if not request.json:
        abort(400)

    author = g.user
    tags = request.json.get('tags')
    title = request.json.get('title')
    content = request.json.get('content')
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    if not title or not content:
        abort(400)

    blogpost = BlogPost(author=author.id, title=title, content=content,
                        created_at=created_at, updated_at=updated_at)
    if tags:
        blogpost.tags = tags
    db.session.add(blogpost)
    db.session.commit()

    return jsonify({
        'status': 'Created',
        'code': 201,
        'message': "Blog post created!"}), 201


@app.route('/api/blogposts')
def get_blogposts():
    blogposts = BlogPost.query.all()
    data = []

    for blogpost in blogposts:
        author = User.query.filter_by(id=blogpost.author).first()
        data.append({
            'id': blogpost.id,
            'author': author.username,
            'tags': blogpost.tags,
            'title': blogpost.title,
            'content': blogpost.content,
            'created_at': blogpost.created_at,
            'updated_at': blogpost.updated_at
        })

    return jsonify(blogpostlar=data), 200


@app.route('/api/blogposts/<int:id>')
def get_blogpost(id):
    blogpost = BlogPost.query.filter_by(id=id).first()

    if not blogpost:
        abort(404)
    author = User.query.filter_by(id=blogpost.author).first()

    data = {
        'id': blogpost.id,
        'author': author.username,
        'tags': blogpost.tags,
        'title': blogpost.title,
        'content': blogpost.content,
        'created_at': blogpost.created_at,
        'updated_at': blogpost.updated_at
    }

    return jsonify(data), 200


@app.route('/api/blogposts/<int:id>', methods=['DELETE'])
@AuthenticationRequired
def delete_blogpost(id):
    blogpost = BlogPost.query.filter_by(id=id)

    if not blogpost.first():
        abort(404)
    print(blogpost.first().author)
    if int(blogpost.first().author) is not g.user.id:
        abort(403, 'You are forbidden to delete this blog post.')

    db.session.delete(blogpost.first())
    db.session.commit()

    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Blog post deleted."
    }), 200


@app.route('/api/blogposts/<int:id>', methods=['PATCH'])
@AuthenticationRequired
def update_blogpost(id):
    blogpost = BlogPost.query.filter_by(id=id)

    if not blogpost.first():
        abort(404, "Blog post not found")

    if int(blogpost.first().author) is not g.user.id:
        abort(403, 'You are forbidden to update this blog post.')

    if not request.json:
        abort(400)

    if request.json.get('title'):
        blogpost.first().title = request.json.get('title')
    if request.json.get('content'):
        blogpost.first().content = request.json.get('content')
    if request.json.get('tags'):
        blogpost.first().tags = request.json.get('tags')
    blogpost.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Blog post updated"
    }), 200


@app.errorhandler(400)
def custom400(error):
    return jsonify({
        "name": API_NAME,
        "status": "Bad Request",
        "code": 400,
        "message": error.description
    }), 400


@app.errorhandler(401)
def custom401(error):
    return jsonify({
        "name": API_NAME,
        "status": "Unauthorized",
        "code": 401,
        "message": error.description
    }), 401


@app.errorhandler(403)
def custom403(error):
    return jsonify({
        "name": API_NAME,
        "status": "Forbidden",
        "code": 403,
        "message": error.description
    }), 403


@app.errorhandler(404)
def custom404(error):
    return jsonify({
        "name": API_NAME,
        "status": "Not Found",
        "code": 404,
        "message": error.description
    }), 404


@app.errorhandler(405)
def custom405(error):
    return jsonify({
        "name": API_NAME,
        "status": "Method Not Allowed",
        "code": 405,
        "message": error.description
    }), 405


if __name__:
    app.run(debug=True)
    db.create_all()
