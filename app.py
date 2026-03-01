import json
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / 'data' / 'emitters.sqlite'
PUBLIC_DIR = ROOT / 'public'


def ensure_schema(cur: sqlite3.Cursor) -> None:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emitters'")
    exists = cur.fetchone() is not None
    if exists:
        cur.execute("PRAGMA table_info(emitters)")
        column_names = [row[1] for row in cur.fetchall()]
        if 'priValues' not in column_names or 'pwValues' not in column_names:
            cur.execute('DROP TABLE emitters')

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS emitters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            minFreq REAL NOT NULL,
            maxFreq REAL NOT NULL,
            centerFreq REAL NOT NULL,
            frequencyType TEXT NOT NULL,
            priValues TEXT NOT NULL,
            priType TEXT NOT NULL,
            signalAmplitude REAL NOT NULL,
            pwValues TEXT NOT NULL,
            pwType TEXT NOT NULL,
            firstSeen TEXT NOT NULL,
            lastSeen TEXT NOT NULL,
            intraPulseModulation TEXT NOT NULL
        )
        '''
    )


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ensure_schema(cur)

    cur.execute('SELECT COUNT(*) FROM emitters')
    if cur.fetchone()[0] == 0:
        rows = [
            ('Emitter-01', 920, 980, 950, 'Constant', [780, 812, 835], 'Constant', -45, [1.8, 2.0, 2.1, 2.2], 'Narrow', '2026-02-01T08:15:00Z', '2026-02-01T11:10:00Z', 'Linear FM'),
            ('Emitter-02', 1050, 1190, 1120, 'Agile', [590, 615, 640, 668, 690], 'Jittered', -52, [2.8, 3.2, 3.5], 'Medium', '2026-02-01T09:05:00Z', '2026-02-01T11:22:00Z', 'Phase Coded'),
            ('Emitter-03', 1250, 1380, 1315, 'Hopping', [480, 510, 540, 565], 'Staggered', -50, [1.2, 1.5, 1.7, 1.9, 2.1], 'Narrow', '2026-02-01T09:20:00Z', '2026-02-01T10:58:00Z', 'Barker 13'),
            ('Emitter-04', 760, 880, 820, 'Constant', [930, 955, 980, 1010, 1030, 1050], 'Dwell/Switch', -48, [3.8, 4.0, 4.2], 'Wide', '2026-02-01T07:40:00Z', '2026-02-01T10:15:00Z', 'None'),
            ('Emitter-05', 1410, 1580, 1495, 'Agile', [670, 690, 710], 'Jittered', -53, [2.4, 2.6, 2.8, 3.0, 3.3, 3.5], 'Medium', '2026-02-01T08:55:00Z', '2026-02-01T11:35:00Z', 'Quadratic FM'),
            ('Emitter-06', 1660, 1790, 1725, 'Hopping', [410, 430, 460, 490, 520], 'Staggered', -55, [0.9, 1.0, 1.2, 1.4], 'Narrow', '2026-02-01T10:00:00Z', '2026-02-01T11:50:00Z', 'Polyphase'),
            ('Emitter-07', 610, 735, 672.5, 'Constant', [1150, 1190, 1230, 1270], 'Constant', -42, [4.6, 4.9, 5.1, 5.4], 'Wide', '2026-02-01T06:25:00Z', '2026-02-01T10:20:00Z', 'None'),
            ('Emitter-08', 1820, 1960, 1890, 'Agile', [620, 650, 690, 730, 760, 790], 'Dwell/Switch', -57, [2.1, 2.3, 2.4], 'Medium', '2026-02-01T09:45:00Z', '2026-02-01T11:40:00Z', 'Costas'),
            ('Emitter-09', 1980, 2130, 2055, 'Hopping', [460, 485, 510, 535, 560], 'Staggered', -54, [1.4, 1.6, 1.9], 'Narrow', '2026-02-01T10:12:00Z', '2026-02-01T11:55:00Z', 'FSK Intra-Pulse'),
            ('Emitter-10', 860, 1040, 950, 'Agile', [700, 730, 760, 790], 'Jittered', -49, [2.6, 2.9, 3.1, 3.4, 3.7], 'Medium', '2026-02-01T07:55:00Z', '2026-02-01T11:12:00Z', 'Stepped FM'),
        ]

        payload_rows = [
            (
                name,
                min_freq,
                max_freq,
                center_freq,
                frequency_type,
                json.dumps(pri_values),
                pri_type,
                signal_amplitude,
                json.dumps(pw_values),
                pw_type,
                first_seen,
                last_seen,
                intra_pulse_mod,
            )
            for (
                name,
                min_freq,
                max_freq,
                center_freq,
                frequency_type,
                pri_values,
                pri_type,
                signal_amplitude,
                pw_values,
                pw_type,
                first_seen,
                last_seen,
                intra_pulse_mod,
            ) in rows
        ]

        cur.executemany(
            '''
            INSERT INTO emitters (
                name, minFreq, maxFreq, centerFreq, frequencyType, priValues,
                priType, signalAmplitude, pwValues, pwType, firstSeen,
                lastSeen, intraPulseModulation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            payload_rows,
        )

    conn.commit()
    conn.close()


def get_emitters() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM emitters ORDER BY id')

    rows = []
    for row in cur.fetchall():
        item = dict(row)
        item['priValues'] = json.loads(item['priValues'])
        item['pwValues'] = json.loads(item['pwValues'])
        rows.append(item)

    conn.close()
    return rows


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/api/emitters':
            data = json.dumps(get_emitters()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


if __name__ == '__main__':
    init_db()
    server = ThreadingHTTPServer(('0.0.0.0', 3000), Handler)
    print('Emitter dashboard running on http://localhost:3000')
    server.serve_forever()
