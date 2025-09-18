import sqlite3
import pandas as pd
from datetime import datetime
import json

DB_PATH = 'muyu_demo.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Institution
    cur.execute('''
    CREATE TABLE IF NOT EXISTS institution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT,
        city TEXT
    )
    ''')
    # Demo
    cur.execute('''
    CREATE TABLE IF NOT EXISTS demo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institution_id INTEGER,
        title TEXT,
        responsable_muyu TEXT,
        num_users INTEGER DEFAULT 0,
        state TEXT,
        phase TEXT,
        start_date TEXT,
        start_phase_date TEXT,
        end_phase_date TEXT,
        end_date TEXT,
        metadata TEXT,
        FOREIGN KEY(institution_id) REFERENCES institution(id)
    )
    ''')
    # Participant (docente)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS participant (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        demo_id INTEGER,
        name TEXT,
        email TEXT,
        phone TEXT,
        activated INTEGER DEFAULT 0,
        recordings_count INTEGER DEFAULT 0,
        survey_response INTEGER DEFAULT 0,
        FOREIGN KEY(demo_id) REFERENCES demo(id)
    )
    ''')
    # Tasks / Automations / Alerts
    cur.execute('''
    CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        demo_id INTEGER,
        title TEXT,
        description TEXT,
        created_at TEXT,
        done INTEGER DEFAULT 0,
        assigned_to TEXT,
        type TEXT,
        FOREIGN KEY(demo_id) REFERENCES demo(id)
    )
    ''')
    # Audit log
    cur.execute('''
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        who TEXT,
        action TEXT,
        ts TEXT,
        details TEXT
    )
    ''')
    # Roles
    cur.execute('''
    CREATE TABLE IF NOT EXISTS role (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    # Users
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT
    )
    ''')
    # Contact (asegura que la columna institution_id exista)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS contact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    )
    ''')
    # Migración: agrega institution_id si no existe
    cur.execute("PRAGMA table_info(contact)")
    columns = [row[1] for row in cur.fetchall()]
    if "institution_id" not in columns:
        cur.execute("ALTER TABLE contact ADD COLUMN institution_id INTEGER REFERENCES institution(id)")
        conn.commit()
    conn.commit()
    conn.close()

def seed_if_empty():
    conn = get_conn()
    cur = conn.cursor()
    # Solo agrega instituciones si la tabla está vacía (esto es correcto para datos demo)
    cur.execute('SELECT COUNT(*) as c FROM institution')
    if cur.fetchone()['c'] == 0:
        cur.execute('INSERT INTO institution (name, country, city) VALUES (?,?,?)',
                    ('Colegio Demo San Carlos', 'Ecuador', 'Manta'))
        cur.execute('INSERT INTO institution (name, country, city) VALUES (?,?,?)',
                    ('Instituto Demo Norte', 'Ecuador', 'Portoviejo'))
        conn.commit()
    cur.execute('SELECT COUNT(*) as c FROM demo')
    if cur.fetchone()['c'] == 0:
        now = datetime.utcnow().isoformat()
        cur.execute('INSERT INTO demo (institution_id, title, responsable_muyu, num_users, state, phase, start_date, metadata) VALUES (?,?,?,?,?,?,?,?)',
                    (1, 'Demo 4 semanas - San Carlos', 'Imanol', 10, 'Preparaci\u00f3n', 'Inicio', now, json.dumps({})))
        demo_id = cur.lastrowid
        participants = [
            ('Ana Perez','ana@demo.edu','0999000001'),
            ('Luis Gomez','luis@demo.edu','0999000002'),
            ('Mar\u00eda Ruiz','maria@demo.edu','0999000003')
        ]
        for p in participants:
            cur.execute('INSERT INTO participant (demo_id, name, email, phone, activated) VALUES (?,?,?,?,?)',
                        (demo_id, p[0], p[1], p[2], 0))
        conn.commit()
    # Seed roles
    cur.execute('SELECT COUNT(*) as c FROM role')
    if cur.fetchone()['c'] == 0:
        cur.execute('INSERT INTO role (name) VALUES (?)', ('admin',))
        cur.execute('INSERT INTO role (name) VALUES (?)', ('comercial',))
        cur.execute('INSERT INTO role (name) VALUES (?)', ('soporte',))
        conn.commit()
    # Seed admin user
    cur.execute('SELECT COUNT(*) as c FROM user WHERE username=?', ('admin',))
    if cur.fetchone()['c'] == 0:
        cur.execute('INSERT INTO user (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
        conn.commit()
    conn.close()

def fetch_demos():
    conn = get_conn()
    df = pd.read_sql_query('SELECT d.*, i.name as institution_name FROM demo d LEFT JOIN institution i ON d.institution_id=i.id', conn)
    conn.close()
    return df

def fetch_participants(demo_id):
    conn = get_conn()
    df = pd.read_sql_query('SELECT * FROM participant WHERE demo_id=?', conn, params=(demo_id,))
    conn.close()
    return df

def create_demo(institution_id, title, responsable, num_users, start_date=None):
    conn = get_conn()
    cur = conn.cursor()
    start_date = (start_date or datetime.utcnow().isoformat())
    cur.execute('INSERT INTO demo (institution_id, title, responsable_muyu, num_users, state, phase, start_date, metadata) VALUES (?,?,?,?,?,?,?,?)',
                (institution_id, title, responsable, num_users, 'Preparaci\u00f3n', 'Inicio', start_date, json.dumps({})))
    conn.commit()
    conn.close()

def add_participant(demo_id, name, email, phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO participant (demo_id, name, email, phone, activated) VALUES (?,?,?,?,?)',
                (demo_id, name, email, phone, 0))
    conn.commit()
    conn.close()

def update_demo_state(demo_id, new_state, who='system'):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('UPDATE demo SET state=?, start_phase_date=? WHERE id=?', (new_state, now, demo_id))
    cur.execute('INSERT INTO audit (who, action, ts, details) VALUES (?,?,?,?)', (who, f'state_change:{new_state}', now, f'demo_id={demo_id}'))
    conn.commit()
    conn.close()

def compute_metrics(demo_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as total FROM participant WHERE demo_id=?', (demo_id,))
    total = cur.fetchone()['total']
    cur.execute('SELECT COUNT(*) as active FROM participant WHERE demo_id=? AND activated=1', (demo_id,))
    active = cur.fetchone()['active']
    cur.execute('SELECT COUNT(*) as recs FROM participant WHERE demo_id=? AND recordings_count>0', (demo_id,))
    recs = cur.fetchone()['recs']
    cur.execute('SELECT COUNT(*) as surveys FROM participant WHERE demo_id=? AND survey_response=1', (demo_id,))
    surveys = cur.fetchone()['surveys']
    conn.close()
    activation_pct = (active / total * 100) if total>0 else 0
    recordings_pct = (recs / active * 100) if active>0 else 0
    survey_pct = (surveys / active * 100) if active>0 else 0
    return {
        'total': total,
        'active': active,
        'activation_pct': round(activation_pct,1),
        'recs': recs,
        'recordings_pct': round(recordings_pct,1),
        'surveys': surveys,
        'survey_pct': round(survey_pct,1)
    }

def run_automation_checks(demo_id, config=None):
    cfg = config or {}
    activation_th = cfg.get('activation_th', 60)
    recordings_th = cfg.get('recordings_th', 50)
    survey_th = cfg.get('survey_th', 70)
    metrics = compute_metrics(demo_id)
    alerts = []
    if metrics['activation_pct'] < activation_th:
        alerts.append({'level':1, 'code':'activation_low', 'msg':f'Activaci\u00f3n baja: {metrics["activation_pct"]}% < {activation_th}%.'})
    if metrics['recordings_pct'] < recordings_th:
        alerts.append({'level':1, 'code':'recordings_low', 'msg':f'Grabaciones bajas: {metrics["recordings_pct"]}% < {recordings_th}%.'})
    if metrics['survey_pct'] < survey_th:
        alerts.append({'level':1, 'code':'survey_low', 'msg':f'Encuesta baja: {metrics["survey_pct"]}% < {survey_th}%.'})
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    for a in alerts:
        cur.execute('INSERT INTO task (demo_id, title, description, created_at, done, assigned_to, type) VALUES (?,?,?,?,?,?,?)',
                    (demo_id, f'ALERTA: {a["code"]}', a['msg'], now, 0, 'Coordinador', 'alert'))
    conn.commit()
    conn.close()
    return alerts
