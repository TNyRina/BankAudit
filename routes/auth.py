from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import hashlib
import sqlite3
from db import get_db

bp_auth = Blueprint('bp_auth',__name__)

def hash_password(password: str) -> str:
    """SHA-256 + sel simple. En production, utilisez bcrypt."""
    salt = "bankaudit_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

@bp_auth.route('/')
def index():
    return render_template('auth/index.html', mode='login')

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        if user and user['password'] == hash_password(password):
            session['id_user']  = user['id_user']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Bienvenue, {user['username']} !", 'success')

            if user['role'] == "user" :
                return redirect(url_for('bp_dashboard.index'))
            else :
                return redirect(url_for('bp_audit.audit'))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
            return render_template('auth/index.html', mode='login')


@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'id_user' in session:
        return redirect(url_for('bp_dashboard.index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role     = request.form.get('role', 'user')

        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return render_template('auth/index.html', mode='register')

        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
                (username, hash_password(password), role)
            )
            conn.commit()
            flash(f"Compte {'admin' if role=='admin' else 'utilisateur'} créé ! Connectez-vous.", 'success')
        except sqlite3.IntegrityError:
            flash("Ce nom d'utilisateur est déjà pris.", 'danger')
        finally:
            conn.close()
        
        return render_template('auth/index.html', mode='login')

    return render_template('auth.html', mode='register')


@bp_auth.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('bp_auth.index'))