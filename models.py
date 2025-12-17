from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'role': self.role}

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")
    dislikes = db.relationship('Dislike', backref='post', lazy=True, cascade="all, delete-orphan")

    def likes_count(self):
        return db.session.query(Like).filter_by(post_id=self.id).count()

    def dislikes_count(self):
        return db.session.query(Dislike).filter_by(post_id=self.id).count()

    def user_liked(self, user_id):
        if user_id is None:
            return False
        return db.session.query(Like).filter_by(post_id=self.id, user_id=user_id).first() is not None

    def user_disliked(self, user_id):
        if user_id is None:
            return False
        return db.session.query(Dislike).filter_by(post_id=self.id, user_id=user_id).first() is not None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() + 'Z',
            'author': self.author.username,
            'author_id': self.author.id
        }

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_like'),)

class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_dislike'),)