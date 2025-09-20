# Gratitude Journal — Production-ready Scaffold

This document contains a complete repository scaffold for a production-ready Gratitude Journal web app using **Flask + Postgres + Gunicorn + Nginx + Docker Compose**. Copy the files into a repo and follow the **Quick start** section below.

---

## Quick start

1. Copy the files in this doc into a repository (preserve the file paths).
2. Create a `.env` file from `.env.example` and set strong secrets (do **not** commit `.env`).
3. Build and start:

```bash
docker-compose build
docker-compose up -d
# run migrations
docker-compose exec web flask db upgrade
```

4. Point DNS (your.domain) to the server and configure TLS (Certbot / Traefik — see README below).

---

## File tree

```
gratitude-prod/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── gunicorn.conf.py
├── nginx/default.conf
├── requirements.txt
├── manage.py
├── run.sh
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── auth.py
│   ├── entries.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── journal.html
│   └── static/
│       └── style.css
└── nginx/
    └── default.conf
```

---

## `README.md`

```markdown
# Gratitude Journal — Production Scaffold

Flask app with Postgres, Gunicorn, Nginx, and Docker Compose.

## Features
- User registration & login
- Per-user gratitude entries
- PostgreSQL with migrations (Flask-Migrate / Alembic)
- Gunicorn + Nginx (reverse proxy)
- Dockerized for easy deployment

## Local development
1. Copy `.env.example` to `.env` and set values.
2. `docker-compose build && docker-compose up -d`
3. `docker-compose exec web flask db upgrade`
4. Open http://localhost:8000 (Nginx proxies to Gunicorn)

## Production notes
- Use strong `SECRET_KEY` and DB password; store secrets in a secret manager.
- Configure TLS via Certbot on the host or use Traefik for automated certs.
- Backup Postgres volume regularly.

```

````

---

## `.env.example`

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=replace_this_with_a_strong_secret

# Postgres
POSTGRES_DB=gratitude
POSTGRES_USER=gratuser
POSTGRES_PASSWORD=change_this_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://gratuser:change_this_password@db:5432/gratitude

# App
APP_HOST=0.0.0.0
APP_PORT=8000

# Gunicorn
GUNICORN_WORKERS=3
````

---

## `.gitignore`

```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.env
venv/
instance/
*.sqlite3
*.log
docker-compose.override.yml

```

---

## `docker-compose.yml`

```yaml
version: '3.8'
services:
  web:
    build: .
    env_file: .env
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    networks:
      - gjnet

  db:
    image: postgres:15
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    networks:
      - gjnet

  nginx:
    image: nginx:stable
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./app/static:/app/app/static:ro
      - ./letsencrypt:/etc/letsencrypt
    depends_on:
      - web
    networks:
      - gjnet

volumes:
  pgdata:

networks:
  gjnet:
    driver: bridge
```

---

## `Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# create non-root user
RUN useradd -m appuser || true
RUN chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "manage:app", "-c", "gunicorn.conf.py"]
```

---

## `gunicorn.conf.py`

```python
bind = "0.0.0.0:8000"
workers = int(__import__('os').environ.get('GUNICORN_WORKERS', '3'))
timeout = 30
worker_class = 'gthread'
threads = 4
accesslog = '-'
errorlog = '-'
```

---

## `nginx/default.conf`

```nginx
server {
    listen 80;
    server_name your.domain.example; # change this

    location /static/ {
        alias /app/app/static/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## `requirements.txt`

```text
Flask==2.3.2
Flask-Login==0.6.2
Flask-Migrate==4.0.4
Flask-SQLAlchemy==3.0.3
psycopg2-binary==2.9.10
gunicorn==20.1.0
flask-bcrypt==1.0.1
python-dotenv==1.0.0
```

---

## `manage.py`

```python
import os
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host=os.environ.get('APP_HOST', '0.0.0.0'), port=int(os.environ.get('APP_PORT', 8000)))
```

---

## `run.sh` (helper for local dev)

```bash
#!/usr/bin/env bash
set -e

export FLASK_APP=manage.py
export FLASK_ENV=development

flask db upgrade || true
flask run --host=0.0.0.0 --port=5000
```

Make executable: `chmod +x run.sh`

---

## `app/__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bcrypt = Bcrypt()


def create_app(config_object=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object or 'app.config.ProductionConfig')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bcrypt.init_app(app)

    # register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .entries import bp as entries_bp
    app.register_blueprint(entries_bp)

    # simple index route
    @app.route('/ping')
    def ping():
        return 'pong'

    return app
```

---

## `app/config.py`

```python
import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
```

---

## `app/models.py`

```python
from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    entries = db.relationship('Entry', backref='user', lazy=True)

    def set_password(self, password, bcrypt):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, password)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

---

## `app/auth.py`

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db, login, bcrypt
from .models import User
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        user = User(username=username)
        user.set_password(password, bcrypt)
        db.session.add(user)
        db.session.commit()
        flash('Account created — please log in')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password, bcrypt):
            login_user(user)
            return redirect(url_for('entries.index'))
        flash('Invalid credentials')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# needed by Flask-Login
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

---

## `app/entries.py`

```python
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Entry

bp = Blueprint('entries', __name__)

@bp.route('/')
@login_required
def index():
    entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.created_at.desc()).all()
    return render_template('journal.html', entries=entries, user=current_user)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    content = request.form.get('content')
    if content:
        e = Entry(content=content, user_id=current_user.id)
        db.session.add(e)
        db.session.commit()
    return redirect(url_for('entries.index'))
```

---

## Templates

### `app/templates/base.html`

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gratitude Journal</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <na
```
