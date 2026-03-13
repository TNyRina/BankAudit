import sqlite3

DB_PATH = 'bank.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Tables
    c.executescript('''
        CREATE TABLE IF NOT EXISTS user (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );            

        CREATE TABLE IF NOT EXISTS client (
            n_compte TEXT PRIMARY KEY,
            nomclient TEXT NOT NULL,
            solde REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS virement (
            n_virement INTEGER PRIMARY KEY AUTOINCREMENT,
            n_compte TEXT NOT NULL,
            id_user TEXT NOT NULL,
            montant REAL NOT NULL,
            date_virement TEXT NOT NULL,
            FOREIGN KEY (n_compte) REFERENCES client(n_compte),
            FOREIGN KEY (id_user) REFERENCES user(id_user)
        );

        CREATE TABLE IF NOT EXISTS audit_virement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_action TEXT NOT NULL,
            date_operation TEXT NOT NULL,
            n_virement INTEGER,
            n_compte TEXT,
            nomclient TEXT,
            date_virement TEXT,
            montant_ancien REAL,
            montant_nouv REAL,
            utilisateur TEXT NOT NULL
        );
    ''')

    # Trigger INSERT
    c.execute("DROP TRIGGER IF EXISTS trg_after_insert_virement")
    c.execute('''
        CREATE TRIGGER trg_after_insert_virement
        AFTER INSERT ON virement
        BEGIN
            UPDATE client
            SET solde = solde + NEW.montant
            WHERE n_compte = NEW.n_compte;

            INSERT INTO audit_virement (
                type_action, date_operation, n_virement, n_compte,
                nomclient, date_virement, montant_nouv, utilisateur
            )
            SELECT
                'ajout',
                datetime('now'),
                NEW.n_virement,
                NEW.n_compte,
                c.nomclient,
                NEW.date_virement,
                NEW.montant,
                NEW.id_user
            FROM client c WHERE c.n_compte = NEW.n_compte;
        END;
    ''')

    # Trigger UPDATE
    c.execute("DROP TRIGGER IF EXISTS trg_after_update_virement")
    c.execute('''
        CREATE TRIGGER trg_after_update_virement
        AFTER UPDATE ON virement
        BEGIN
            UPDATE client
            SET solde = solde - OLD.montant + NEW.montant
            WHERE n_compte = NEW.n_compte;

            INSERT INTO audit_virement (
                type_action, date_operation, n_virement, n_compte,
                nomclient, date_virement, montant_ancien, montant_nouv, utilisateur
            )
            SELECT
                'modification',
                datetime('now'),
                NEW.n_virement,
                NEW.n_compte,
                c.nomclient,
                NEW.date_virement,
                OLD.montant,
                NEW.montant,
                NEW.id_user
            FROM client c WHERE c.n_compte = NEW.n_compte;
        END;
    ''')

    # Trigger DELETE
    c.execute("DROP TRIGGER IF EXISTS trg_after_delete_virement")
    c.execute('''
        CREATE TRIGGER trg_after_delete_virement
        AFTER DELETE ON virement
        BEGIN
            UPDATE client
            SET solde = solde - OLD.montant
            WHERE n_compte = OLD.n_compte;

            INSERT INTO audit_virement (
                type_action, date_operation, n_virement, n_compte,
                nomclient, date_virement, montant_ancien, utilisateur
            )
            SELECT
                'suppression',
                datetime('now'),
                OLD.n_virement,
                OLD.n_compte,
                c.nomclient,
                OLD.date_virement,
                OLD.montant,
                OLD.id_user
            FROM client c WHERE c.n_compte = OLD.n_compte;
        END;
    ''')

    # Sample data
    c.execute("SELECT COUNT(*) FROM client")
    if c.fetchone()[0] == 0:
        c.executescript('''
            INSERT INTO client VALUES ('C001', 'Jean Dupont', 5000.00);
            INSERT INTO client VALUES ('C002', 'Marie Martin', 8500.00);
            INSERT INTO client VALUES ('C003', 'Paul Bernard', 3200.00);
        ''')

    conn.commit()
    conn.close()
