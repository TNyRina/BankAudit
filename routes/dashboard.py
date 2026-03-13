from flask import Blueprint, render_template
from decorators import login_required
from db import get_db

bp_dashboard = Blueprint('bp_dashboard', __name__)

@bp_dashboard.route('/dashboard')
@login_required
def index():
    conn = get_db()
    clients = conn.execute('SELECT * FROM client ORDER BY n_compte').fetchall()
    conn.close()
    return render_template('index.html', clients=clients)