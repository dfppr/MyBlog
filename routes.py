from flask import Blueprint, request, jsonify, session
from models import db, User, Post, Like, Dislike

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Нужны имя, email и пароль'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Пользователь с таким email уже существует'}), 400

    new_user = User(username=data['username'], email=data['email'], role='user')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Пользователь создан!'}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Нужны email и пароль'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Неверные учетные данные'}), 401

    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'message': 'Вход выполнен!', 'user': user.to_dict()})

@api_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Выход выполнен'})

@api_bp.route('/posts', methods=['GET'])
def get_all_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    current_user_id = session.get('user_id')
    for p in posts:
        d = p.to_dict()
        d['likes'] = p.likes_count()
        d['dislikes'] = p.dislikes_count()
        d['user_liked'] = p.user_liked(current_user_id)
        d['user_disliked'] = p.user_disliked(current_user_id)
        result.append(d)
    return jsonify(result)

@api_bp.route('/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'message': 'Не авторизовано'}), 401

    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'message': 'Нужны заголовок и содержимое'}), 400

    new_post = Post(title=data['title'], content=data['content'], user_id=session['user_id'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Пост создан!', 'post': new_post.to_dict()}), 201

@api_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Не авторизовано'}), 401

    post = Post.query.get_or_404(post_id)

    if session['role'] != 'admin' and post.user_id != session['user_id']:
        return jsonify({'message': 'Доступ запрещен'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Пост удален'})

@api_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Не авторизовано'}), 401

    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if like:
        db.session.delete(like)
    else:
        new_like = Like(post_id=post_id, user_id=session['user_id'])
        db.session.add(new_like)

    db.session.commit()

    return jsonify({
        'likes': post.likes_count(),
        'dislikes': post.dislikes_count(),
        'user_liked': post.user_liked(session['user_id']),
        'user_disliked': post.user_disliked(session['user_id'])
    })

@api_bp.route('/posts/<int:post_id>/dislike', methods=['POST'])
def dislike_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Не авторизовано'}), 401

    post = Post.query.get_or_404(post_id)
    dislike = Dislike.query.filter_by(post_id=post_id, user_id=session['user_id']).first()

    if dislike:
        db.session.delete(dislike)
    else:
        new_dislike = Dislike(post_id=post_id, user_id=session['user_id'])
        db.session.add(new_dislike)

    db.session.commit()

    return jsonify({
        'likes': post.likes_count(),
        'dislikes': post.dislikes_count(),
        'user_liked': post.user_liked(session['user_id']),
        'user_disliked': post.user_disliked(session['user_id'])
    })