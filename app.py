from flask import Flask,flash, session,  render_template
from db import init_db
from routes.audit import bp_audit
from routes.dashboard import bp_dashboard
from routes.client import bp_client
from routes.virement import bp_virement
from routes.auth import bp_auth
from functools import wraps

app = Flask(__name__)
app.secret_key = 'bank_secret_key_2024'


# Blueprint for routing
app.register_blueprint(bp_auth)
app.register_blueprint(bp_audit)
app.register_blueprint(bp_dashboard)
app.register_blueprint(bp_client)
app.register_blueprint(bp_virement)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
