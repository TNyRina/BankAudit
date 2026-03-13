# BankAudit — Sujet 22

Application Flask de gestion des virements bancaires avec triggers SQLite.

## Installation & Lancement

```bash
pip install flask
python app.py
```

Puis ouvrir : http://127.0.0.1:5000

```

## Tables SQL

```sql
CREATE TABLE client (
    n_compte TEXT PRIMARY KEY,
    nomclient TEXT NOT NULL,
    solde REAL NOT NULL DEFAULT 0
);

CREATE TABLE virement (
    n_virement INTEGER PRIMARY KEY AUTOINCREMENT,
    n_compte TEXT NOT NULL,
    montant REAL NOT NULL,
    date_virement TEXT NOT NULL,
    FOREIGN KEY (n_compte) REFERENCES client(n_compte)
);

CREATE TABLE audit_virement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_action TEXT NOT NULL,       -- ajout | modification | suppression
    date_operation TEXT NOT NULL,
    n_virement INTEGER,
    n_compte TEXT,
    nomclient TEXT,
    date_virement TEXT,
    montant_ancien REAL,
    montant_nouv REAL,
    utilisateur TEXT NOT NULL
);
```

## Triggers

### AFTER INSERT
- Met à jour le solde : `solde = solde + NEW.montant`
- Enregistre dans audit_virement avec type_action = 'ajout'

### AFTER UPDATE
- Recalcule le solde : `solde = solde - OLD.montant + NEW.montant`
- Enregistre avec type_action = 'modification'

### AFTER DELETE
- Soustrait le montant : `solde = solde - OLD.montant`
- Enregistre avec type_action = 'suppression'

## Formule solde
```
Nouveau solde = Ancien solde + Montant
```
