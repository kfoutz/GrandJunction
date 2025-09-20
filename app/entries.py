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