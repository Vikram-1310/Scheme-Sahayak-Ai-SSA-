import sqlite3
from pathlib import Path
from backend.database import DATABASE_FILE

def get_connection():
 c=sqlite3.connect(DATABASE_FILE); c.row_factory=sqlite3.Row; return c

def initialize_application_table():
 c=get_connection(); c.execute('''CREATE TABLE IF NOT EXISTS applications(
 id INTEGER PRIMARY KEY AUTOINCREMENT, beneficiary_id INTEGER NOT NULL, scheme_id TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'submitted', notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(beneficiary_id) REFERENCES beneficiaries(id))'''); c.commit(); c.close()

def create_application(beneficiary_id, scheme_id, notes=None):
 c=get_connection(); b=c.execute('SELECT id FROM beneficiaries WHERE id=?',(beneficiary_id,)).fetchone()
 if not b: c.close(); return None
 cur=c.execute("INSERT INTO applications(beneficiary_id,scheme_id,status,notes) VALUES(?,?, 'submitted',?)",(beneficiary_id,scheme_id,notes)); c.commit(); i=cur.lastrowid; c.close(); return get_application(i)

def get_application(application_id):
 c=get_connection(); r=c.execute('SELECT * FROM applications WHERE id=?',(application_id,)).fetchone(); c.close(); return dict(r) if r else None

def application_owned_by_user(application_id,user_id):
 c=get_connection(); r=c.execute('''SELECT a.* FROM applications a JOIN beneficiaries b ON b.id=a.beneficiary_id WHERE a.id=? AND b.user_id=?''',(application_id,user_id)).fetchone(); c.close(); return dict(r) if r else None

def update_application_status(application_id,status,notes=None):
 c=get_connection(); cur=c.execute('UPDATE applications SET status=?,notes=COALESCE(?,notes),updated_at=CURRENT_TIMESTAMP WHERE id=?',(status,notes,application_id)); c.commit(); ok=cur.rowcount>0; c.close(); return get_application(application_id) if ok else None

def get_beneficiary_applications(beneficiary_id):
 c=get_connection(); rows=c.execute('SELECT * FROM applications WHERE beneficiary_id=? ORDER BY created_at DESC',(beneficiary_id,)).fetchall(); c.close(); return [dict(r) for r in rows]
