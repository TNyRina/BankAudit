from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from decorators import login_required
from db import get_db

bp_client = Blueprint('bp_client', __name__)

@bp_client.route('/clients')
@login_required
def clients():
    conn = get_db()
    rows = conn.execute('SELECT * FROM client ORDER BY n_compte').fetchall()
    conn.close()
    return render_template('clients.html', clients=rows)

@bp_client.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        n = request.form['n_compte'].strip()
        nom = request.form['nomclient'].strip()
        solde = float(request.form['solde'])
        conn = get_db()
        try:
            conn.execute('INSERT INTO client VALUES (?, ?, ?)', (n, nom, solde))
            conn.commit()
            flash('Client ajouté avec succès.', 'success')
        except sqlite3.IntegrityError:
            flash('Numéro de compte déjà existant.', 'danger')
        finally:
            conn.close()
        return redirect(url_for('bp_client.clients'))
    return render_template('client_form.html', action='Ajouter', client=None)

@bp_client.route('/clients/edit/<n_compte>', methods=['GET', 'POST'])
@login_required
def edit_client(n_compte):
    conn = get_db()
    client = conn.execute('SELECT * FROM client WHERE n_compte=?', (n_compte,)).fetchone()
    if request.method == 'POST':
        nom = request.form['nomclient'].strip()
        solde = float(request.form['solde'])
        conn.execute('UPDATE client SET nomclient=?, solde=? WHERE n_compte=?', (nom, solde, n_compte))
        conn.commit()
        conn.close()
        flash('Client modifié.', 'success')
        return redirect(url_for('bp_client.clients'))
    conn.close()
    return render_template('client_form.html', action='Modifier', client=client)

@bp_client.route('/clients/delete/<n_compte>', methods=['POST'])
@login_required
def delete_client(n_compte):
    conn = get_db()
    conn.execute('DELETE FROM client WHERE n_compte=?', (n_compte,))
    conn.commit()
    conn.close()
    flash('Client supprimé.', 'warning')
    return redirect(url_for('bp_client.clients'))
