from flask import Flask, render_template
from flask_cors import CORS
from models import db
from routes import api_bp
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Создаём папку для базы, если нет
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data'), exist_ok=True)

db.init_app(app)
CORS(app, supports_credentials=True)  # Важно для сессий

app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.cli.command("init-db")
def init_db_command():
    """Инициализация БД и создание админа"""
    with app.app_context():
        db.create_all()
        from models import User
        if User.query.filter_by(email='admin@example.com').first() is None:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Администратор создан: admin@example.com / admin123')
        else:
            print('База уже инициализирована.')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')