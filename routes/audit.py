from flask import Blueprint, render_template
from db import get_db

bp_audit = Blueprint('bp_audit', __name__)

@bp_audit.route('/audit')
def audit():
    conn = get_db()
    rows = conn.execute('SELECT type_action, date_operation, n_virement, n_compte, nomclient, date_virement, montant_ancien, montant_nouv, user.username as utilisateur FROM audit_virement JOIN user ON audit_virement.utilisateur = user.id_user ORDER BY id DESC').fetchall()
    stats = conn.execute('''
        SELECT
            SUM(CASE WHEN type_action='ajout' THEN 1 ELSE 0 END) as nb_insert,
            SUM(CASE WHEN type_action='modification' THEN 1 ELSE 0 END) as nb_update,
            SUM(CASE WHEN type_action='suppression' THEN 1 ELSE 0 END) as nb_delete
        FROM audit_virement
    ''').fetchone()
    conn.close()
    return render_template('audit.html', audits=rows, stats=stats)