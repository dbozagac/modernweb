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
        required_columns = {
            'emitter_image',
            'country',
            'classification',
            'operatorUnit',
            'platform',
            'missionArea',
            'priValues',
            'pwValues',
            'antennaType',
            'antennaHeightM',
            'antennaGainDbi',
            'antennaPolarization',
            'antennaAzimuthDeg',
            'antennaElevationDeg',
            'beamwidthDeg',
            'bandwidthMHz',
            'txPowerWatts',
            'receiverSensitivityDbm',
        }
        if not required_columns.issubset(column_names):
            cur.execute('DROP TABLE emitters')

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS emitters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            emitter_image TEXT NOT NULL,
            country TEXT NOT NULL,
            classification TEXT NOT NULL,
            operatorUnit TEXT NOT NULL,
            platform TEXT NOT NULL,
            missionArea TEXT NOT NULL,
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
            intraPulseModulation TEXT NOT NULL,
            antennaType TEXT NOT NULL,
            antennaHeightM REAL NOT NULL,
            antennaGainDbi REAL NOT NULL,
            antennaPolarization TEXT NOT NULL,
            antennaAzimuthDeg REAL NOT NULL,
            antennaElevationDeg REAL NOT NULL,
            beamwidthDeg REAL NOT NULL,
            bandwidthMHz REAL NOT NULL,
            txPowerWatts REAL NOT NULL,
            receiverSensitivityDbm REAL NOT NULL
        )
        '''
    )


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ensure_schema(cur)

    cur.execute('SELECT COUNT(*) FROM emitters')
    row_count = cur.fetchone()[0]
    should_seed = row_count == 0
    if row_count > 0:
        cur.execute('SELECT priValues, pwValues, emitter_image FROM emitters ORDER BY id')
        samples = cur.fetchall()
        try:
            parsed = [(json.loads(row[0]), json.loads(row[1]), row[2]) for row in samples]
            first_pri_len = len(parsed[0][0]) if parsed else 0
            min_other_pri_len = min((len(pri) for pri, _, _ in parsed[1:]), default=8)
            min_pw_len = min((len(pw) for _, pw, _ in parsed), default=8)
            missing_image = any((not image or not str(image).strip()) for _, _, image in parsed)
            # First emitter PRI must be 5; others should stay in dense range.
            should_seed = first_pri_len != 5 or min_other_pri_len < 8 or min_pw_len < 8 or missing_image
        except (TypeError, json.JSONDecodeError):
            should_seed = True

    if should_seed:
        if row_count > 0:
            cur.execute('DELETE FROM emitters')
        rows = [
            ('Emitter-01', 'https://commons.wikimedia.org/wiki/Special:FilePath/Radar_antenna.jpg', 'Turkey', 'Friendly', '1st EW Battalion', 'Ground Radar', 'Border Surveillance', 920, 980, 950, 'Constant', [780, 812, 835], 'Constant', -45, [1.8, 2.0, 2.1, 2.2], 'Narrow', '2026-02-01T08:15:00Z', '2026-02-01T11:10:00Z', 'Linear FM', 'Phased Array', 18, 28, 'Horizontal', 45, 2, 3.5, 60, 2200, -98),
            ('Emitter-02', 'https://commons.wikimedia.org/wiki/Special:FilePath/Airport_Surveillance_Radar.jpg', 'Greece', 'Unknown', 'Aegean Sector Ops', 'Naval Fire Control', 'Maritime Patrol', 1050, 1190, 1120, 'Agile', [590, 615, 640, 668, 690], 'Jittered', -52, [2.8, 3.2, 3.5], 'Medium', '2026-02-01T09:05:00Z', '2026-02-01T11:22:00Z', 'Phase Coded', 'Slotted Waveguide', 24, 31, 'Vertical', 82, 1.5, 2.8, 75, 3500, -95),
            ('Emitter-03', 'https://commons.wikimedia.org/wiki/Special:FilePath/C-band_Radar-dish_Antenna.jpg', 'Bulgaria', 'Hostile', 'Northern Air Defense', 'Air Surveillance', 'Airspace Denial', 1250, 1380, 1315, 'Hopping', [480, 510, 540, 565], 'Staggered', -50, [1.2, 1.5, 1.7, 1.9, 2.1], 'Narrow', '2026-02-01T09:20:00Z', '2026-02-01T10:58:00Z', 'Barker 13', 'Yagi Array', 30, 16, 'Dual', 128, 4, 7.0, 48, 900, -101),
            ('Emitter-04', 'https://commons.wikimedia.org/wiki/Special:FilePath/Cobradane.jpg', 'Romania', 'Neutral', 'Coastal Security Wing', 'Coastal Radar', 'Sea-Lane Monitoring', 760, 880, 820, 'Constant', [930, 955, 980, 1010, 1030, 1050], 'Dwell/Switch', -48, [3.8, 4.0, 4.2], 'Wide', '2026-02-01T07:40:00Z', '2026-02-01T10:15:00Z', 'None', 'Parabolic Dish', 36, 34, 'Circular', 205, 0.8, 1.9, 90, 6400, -93),
            ('Emitter-05', 'https://commons.wikimedia.org/wiki/Special:FilePath/Radar_tower_at_RAF_Leeming.jpg', 'Italy', 'Friendly', 'Southern Fleet EW', 'Naval Surveillance', 'Convoy Escort', 1410, 1580, 1495, 'Agile', [670, 690, 710], 'Jittered', -53, [2.4, 2.6, 2.8, 3.0, 3.3, 3.5], 'Medium', '2026-02-01T08:55:00Z', '2026-02-01T11:35:00Z', 'Quadratic FM', 'Conformal Array', 14, 24, 'Horizontal', 160, 3.5, 4.2, 68, 1800, -99),
            ('Emitter-06', 'https://commons.wikimedia.org/wiki/Special:FilePath/Nike_Hercules_IFC_radars.JPG', 'Russia', 'Hostile', 'Black Sea EW Command', 'Ground Jammer', 'Electronic Attack', 1660, 1790, 1725, 'Hopping', [410, 430, 460, 490, 520], 'Staggered', -55, [0.9, 1.0, 1.2, 1.4], 'Narrow', '2026-02-01T10:00:00Z', '2026-02-01T11:50:00Z', 'Polyphase', 'Log-Periodic', 12, 19, 'Vertical', 300, 6.5, 12.0, 55, 2700, -97),
            ('Emitter-07', 'https://commons.wikimedia.org/wiki/Special:FilePath/MMSR_radar.jpg', 'Ukraine', 'Friendly', 'Eastern Defense Grid', 'Counter-Battery Radar', 'Artillery Tracking', 610, 735, 672.5, 'Constant', [1150, 1190, 1230, 1270], 'Constant', -42, [4.6, 4.9, 5.1, 5.4], 'Wide', '2026-02-01T06:25:00Z', '2026-02-01T10:20:00Z', 'None', 'Panel Array', 22, 26, 'Dual', 270, 5.2, 5.8, 84, 4000, -92),
            ('Emitter-08', 'https://commons.wikimedia.org/wiki/Special:FilePath/Bl64_radar.jpg', 'Egypt', 'Unknown', 'Med Theater Control', 'Airborne Early Warning', 'Regional Air Picture', 1820, 1960, 1890, 'Agile', [620, 650, 690, 730, 760, 790], 'Dwell/Switch', -57, [2.1, 2.3, 2.4], 'Medium', '2026-02-01T09:45:00Z', '2026-02-01T11:40:00Z', 'Costas', 'AESA Nose Array', 9, 33, 'Horizontal', 25, 1.2, 2.1, 110, 5200, -94),
            ('Emitter-09', 'https://commons.wikimedia.org/wiki/Special:FilePath/MVAFS_1973_Radar_2.jpg', 'Israel', 'Friendly', 'Integrated Air Shield', 'Missile Guidance', 'Air Defense', 1980, 2130, 2055, 'Hopping', [460, 485, 510, 535, 560], 'Staggered', -54, [1.4, 1.6, 1.9], 'Narrow', '2026-02-01T10:12:00Z', '2026-02-01T11:55:00Z', 'FSK Intra-Pulse', 'Monopulse Array', 27, 35, 'Circular', 342, 7.0, 1.2, 95, 7800, -90),
            ('Emitter-10', 'https://commons.wikimedia.org/wiki/Special:FilePath/Clear_Air_Force_Station_Alaska.jpg', 'United Kingdom', 'Neutral', 'NATO Training Cell', 'Test Range Beacon', 'Calibration Support', 860, 1040, 950, 'Agile', [700, 730, 760, 790], 'Jittered', -49, [2.6, 2.9, 3.1, 3.4, 3.7], 'Medium', '2026-02-01T07:55:00Z', '2026-02-01T11:12:00Z', 'Stepped FM', 'Horn Antenna', 8, 14, 'Linear', 15, 0.5, 18.0, 40, 650, -103),
        ]

        payload_rows = [
            (
                name,
                emitter_image,
                country,
                classification,
                operator_unit,
                platform,
                mission_area,
                min_freq,
                max_freq,
                center_freq,
                frequency_type,
                json.dumps(
                    (
                        pri_values
                        + [int(pri_values[-1] + (18 + (idx % 4) * 4) * i) for i in range(1, 6)]
                    )[:5] if idx == 0 else (
                        pri_values
                        + [int(pri_values[-1] + (18 + (idx % 4) * 4) * i) for i in range(1, 6)]
                    )
                ),
                pri_type,
                signal_amplitude,
                json.dumps(
                    pw_values
                    + [round(pw_values[-1] + (0.18 + (idx % 3) * 0.07) * i, 2) for i in range(1, 6)]
                ),
                pw_type,
                first_seen,
                last_seen,
                intra_pulse_mod,
                antenna_type,
                antenna_height_m,
                antenna_gain_dbi,
                antenna_polarization,
                antenna_azimuth_deg,
                antenna_elevation_deg,
                beamwidth_deg,
                bandwidth_mhz,
                tx_power_watts,
                receiver_sensitivity_dbm,
            )
            for idx, (
                name,
                emitter_image,
                country,
                classification,
                operator_unit,
                platform,
                mission_area,
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
                antenna_type,
                antenna_height_m,
                antenna_gain_dbi,
                antenna_polarization,
                antenna_azimuth_deg,
                antenna_elevation_deg,
                beamwidth_deg,
                bandwidth_mhz,
                tx_power_watts,
                receiver_sensitivity_dbm,
            ) in enumerate(rows)
        ]

        cur.executemany(
            '''
            INSERT INTO emitters (
                name, emitter_image, country, classification, operatorUnit, platform, missionArea,
                minFreq, maxFreq, centerFreq, frequencyType, priValues, priType,
                signalAmplitude, pwValues, pwType, firstSeen, lastSeen, intraPulseModulation,
                antennaType, antennaHeightM, antennaGainDbi, antennaPolarization,
                antennaAzimuthDeg, antennaElevationDeg, beamwidthDeg, bandwidthMHz,
                txPowerWatts, receiverSensitivityDbm
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    server = ThreadingHTTPServer(('0.0.0.0', 4000), Handler)
    print('Emitter dashboard running on http://localhost:4000')
    server.serve_forever()
