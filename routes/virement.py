from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
from decorators import login_required

bp_virement = Blueprint('bp_virement', __name__) 

@bp_virement.route('/virements')
@login_required
def virements():
    conn = get_db()
    rows = conn.execute('''
        SELECT v.*, c.nomclient FROM virement v
        JOIN client c ON v.n_compte = c.n_compte
        ORDER BY v.n_virement DESC
    ''').fetchall()
    clients = conn.execute('SELECT * FROM client').fetchall()
    conn.close()
    return render_template('virements.html', virements=rows, clients=clients)

@bp_virement.route('/virements/add', methods=['GET', 'POST'])
@login_required
def add_virement():
    conn = get_db()
    if request.method == 'POST':
        n_compte = request.form['n_compte']
        montant = float(request.form['montant'])
        date_v = request.form['date_virement']
        user = session.get('id_user')
        conn.execute('INSERT INTO virement (n_compte, montant, date_virement, id_user) VALUES (?, ?, ?,?)',(n_compte, montant, date_v, user))
        conn.commit()
        conn.close()
        flash('Virement ajouté. Solde mis à jour.', 'success')
        return redirect(url_for('bp_virement.virements'))
    clients = conn.execute('SELECT * FROM client').fetchall()
    conn.close()
    return render_template('virement_form.html', action='Ajouter', virement=None, clients=clients)

@bp_virement.route('/virements/edit/<int:n_virement>', methods=['GET', 'POST'])
@login_required
def edit_virement(n_virement):
    conn = get_db()
    v = conn.execute('SELECT * FROM virement WHERE n_virement=?', (n_virement,)).fetchone()
    if request.method == 'POST':
        montant = float(request.form['montant'])
        date_v = request.form['date_virement']
        conn.execute('UPDATE virement SET id_user=?, montant=?, date_virement=? WHERE n_virement=?',
                     (session["id_user"], montant, date_v, n_virement))
        conn.commit()
        conn.close()
        flash('Virement modifié. Solde recalculé.', 'success')
        return redirect(url_for('bp_virement.virements'))
    clients = conn.execute('SELECT * FROM client').fetchall()
    conn.close()
    return render_template('virement_form.html', action='Modifier', virement=v, clients=clients)


@bp_virement.route('/virements/delete/<int:n_virement>', methods=['POST'])
@login_required
def delete_virement(n_virement):
    conn = get_db()
    
    conn.execute(
        'UPDATE virement SET id_user = ? WHERE n_virement = ?',
        (session['id_user'], n_virement)
    )
    
    conn.execute('DELETE FROM virement WHERE n_virement = ?', (n_virement,))
    conn.commit()
    conn.close()

    flash('Virement supprimé. Solde mis à jour.', 'warning')
    return redirect(url_for('bp_virement.virements'))