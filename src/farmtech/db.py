from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from .config import DB_PATH, ROOT

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

@contextmanager
def connection(path=None):
    target = Path(path or DB_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA journal_mode=WAL')
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def initialize(path=None):
    with connection(path) as conn:
        conn.executescript((ROOT / 'sql/schema.sql').read_text())
        conn.execute('INSERT OR IGNORE INTO produtor VALUES (1,?,?)',
                     ('Gabriel Marcolino Ramos', 'Fazenda demonstrativa FarmTech'))
        conn.executemany('INSERT OR IGNORE INTO cultura VALUES (?,?,1)', [(1,'Café'),(2,'Cana-de-açúcar')])

def query(sql, params=(), path=None):
    with connection(path) as conn:
        return [dict(row) for row in conn.execute(sql, params)]

def talhoes(path=None, active=True):
    return query('SELECT t.*, c.nome cultura FROM talhao t JOIN cultura c ON c.id=t.cultura_id '
                 + ('WHERE t.ativo=1 ' if active else '') + 'ORDER BY t.id', path=path)
