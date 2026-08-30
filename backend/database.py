import sqlite3
from pathlib import Path
from contextlib import contextmanager

DATABASE_FILE = Path(__file__).resolve().parent.parent / "data" / "scheme_sahayak.db"

def get_connection():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DATABASE_FILE, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

@contextmanager
def db_session():
    c = get_connection()
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

def initialize_database():
    with db_session() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'beneficiary'
                CHECK(role IN ('beneficiary','officer','admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            category TEXT NOT NULL,
            annual_income REAL NOT NULL CHECK(annual_income >= 0),
            age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 120),
            purpose TEXT NOT NULL,
            gender TEXT,
            state TEXT,
            district TEXT,
            occupation TEXT,
            business_type TEXT,
            business_stage TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
            scheme_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'submitted'
              CHECK(status IN ('submitted','under_review','approved','rejected','completed')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS saved_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            scheme_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, scheme_id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            scheme_id TEXT,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            scheme_id TEXT,
            partner_type TEXT NOT NULL,
            address TEXT,
            state TEXT,
            district TEXT,
            latitude REAL,
            longitude REAL,
            phone TEXT,
            opening_hours TEXT,
            is_verified INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, id);
        CREATE INDEX IF NOT EXISTS idx_partners_geo ON partners(latitude, longitude);
        """)

def create_chat_session(session_id, user_id, scheme_id=None, language="en"):
    with db_session() as c:
        c.execute("""INSERT OR IGNORE INTO chat_sessions(id,user_id,scheme_id,language)
                     VALUES(?,?,?,?)""", (session_id,user_id,scheme_id,language))

def get_chat_session(session_id, user_id):
    c=get_connection()
    row=c.execute("SELECT * FROM chat_sessions WHERE id=? AND user_id=?",(session_id,user_id)).fetchone()
    c.close()
    return dict(row) if row else None

def save_chat_message(session_id, role, content):
    with db_session() as c:
        c.execute("INSERT INTO chat_messages(session_id,role,content) VALUES(?,?,?)",(session_id,role,content))
        c.execute("UPDATE chat_sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?",(session_id,))

def get_chat_messages(session_id, limit=20):
    c=get_connection()
    rows=c.execute("""SELECT role,content,created_at FROM chat_messages
                      WHERE session_id=? ORDER BY id DESC LIMIT ?""",(session_id,limit)).fetchall()
    c.close()
    return [dict(r) for r in reversed(rows)]

def save_scheme(user_id, scheme_id):
    with db_session() as c:
        c.execute("INSERT OR IGNORE INTO saved_schemes(user_id,scheme_id) VALUES(?,?)",(user_id,scheme_id))

def unsave_scheme(user_id, scheme_id):
    with db_session() as c:
        c.execute("DELETE FROM saved_schemes WHERE user_id=? AND scheme_id=?",(user_id,scheme_id))

def get_saved_schemes(user_id):
    c=get_connection()
    rows=c.execute("SELECT scheme_id,created_at FROM saved_schemes WHERE user_id=? ORDER BY created_at DESC",(user_id,)).fetchall()
    c.close()
    return [dict(r) for r in rows]

def create_beneficiary(user_id, category, annual_income, age, purpose, gender=None,
                       state=None, district=None, occupation=None, business_type=None, business_stage=None):
    with db_session() as c:
        row=c.execute("SELECT id FROM beneficiaries WHERE user_id=?",(user_id,)).fetchone()
        if row:
            c.execute("""UPDATE beneficiaries SET category=?,annual_income=?,age=?,purpose=?,gender=?,
                         state=?,district=?,occupation=?,business_type=?,business_stage=?,updated_at=CURRENT_TIMESTAMP
                         WHERE user_id=?""",
                      (category,annual_income,age,purpose,gender,state,district,occupation,business_type,business_stage,user_id))
            return row["id"]
        cur=c.execute("""INSERT INTO beneficiaries(user_id,category,annual_income,age,purpose,gender,state,district,occupation,business_type,business_stage)
                         VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                      (user_id,category,annual_income,age,purpose,gender,state,district,occupation,business_type,business_stage))
        return cur.lastrowid

def get_beneficiary(beneficiary_id):
    c=get_connection(); row=c.execute("SELECT * FROM beneficiaries WHERE id=?",(beneficiary_id,)).fetchone(); c.close()
    return dict(row) if row else None

def get_beneficiary_for_user(user_id):
    c=get_connection(); row=c.execute("SELECT * FROM beneficiaries WHERE user_id=?",(user_id,)).fetchone(); c.close()
    return dict(row) if row else None

def update_beneficiary(beneficiary_id, user_id, **fields):
    allowed={"category","annual_income","age","purpose","gender","state","district","occupation","business_type","business_stage"}
    values={k:v for k,v in fields.items() if k in allowed}
    if not values: return False
    values["updated_at"]="CURRENT_TIMESTAMP"
    assignments=", ".join(f"{k}=?" for k in values)
    vals=list(values.values())
    # updated_at needs SQL expression, not a bound value
    assignments=assignments.replace("updated_at=?", "updated_at=CURRENT_TIMESTAMP")
    vals=[v for k,v in values.items() if k!="updated_at"]
    with db_session() as c:
        cur=c.execute(f"UPDATE beneficiaries SET {assignments} WHERE id=? AND user_id=?", vals+[beneficiary_id,user_id])
        return cur.rowcount>0


def get_nearby_partners(scheme_id, latitude, longitude, radius_km=50, limit=20):
    """Return verified partners for a scheme, ordered by haversine distance."""
    import math
    c = get_connection()
    rows = c.execute(
        """SELECT * FROM partners
           WHERE is_verified=1
             AND (scheme_id=? OR scheme_id IS NULL)
             AND latitude IS NOT NULL AND longitude IS NOT NULL""",
        (scheme_id,)
    ).fetchall()
    c.close()

    def distance_km(lat1, lon1, lat2, lon2):
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2-lat1)
        dl = math.radians(lon2-lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*r*math.asin(math.sqrt(a))

    result = []
    for row in rows:
        d = distance_km(float(latitude), float(longitude), float(row["latitude"]), float(row["longitude"]))
        if d <= radius_km:
            item = dict(row)
            item["distance_km"] = round(d, 1)
            result.append(item)
    result.sort(key=lambda x: x["distance_km"])
    return result[:limit]
