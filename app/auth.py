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