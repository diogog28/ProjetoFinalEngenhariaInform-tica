"""Modelo relacional SQLite: Sensor (1) -> (N) SensorReading.

SQLite INTEGER PRIMARY KEY gera IDs inteiros. FK impede leituras órfãs.
Não se alteram ficheiros .db antigos automaticamente: usar migrar_legado.py.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('qualidade_ar.db')


def ligar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def inicializar():
    with ligar() as db:
        existente = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='leituras'").fetchone()
        if existente:
            atuais = {r['name'] for r in db.execute('PRAGMA table_info(leituras)')}
            if 'reading_id' not in atuais or 'timestamp_end_UTC' not in atuais:
                raise RuntimeError('SQLite antigo detetado: guarda o .db antigo e reimporta os CSV na nova versão.')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS sensores (
            sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            latitude REAL,
            longitude REAL,
            timezone TEXT NOT NULL DEFAULT 'Europe/Lisbon',
            installation_date TEXT,
            status TEXT NOT NULL DEFAULT 'ativo'
        );
        CREATE TABLE IF NOT EXISTS ficheiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            sensor_id INTEGER NOT NULL,
            importado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sensor_id) REFERENCES sensores(sensor_id)
        );
        CREATE TABLE IF NOT EXISTS leituras (
            reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            ficheiro_id INTEGER NOT NULL,
            timestamp_init_UTC TEXT NOT NULL,
            timestamp_end_UTC TEXT NOT NULL,
            timestamp_init_Europe_Lisbon TEXT NOT NULL,
            timestamp_end_Europe_Lisbon TEXT NOT NULL,
            NO2 REAL, O3 REAL, CO REAL, SO2 REAL, PM1 REAL,
            pressure REAL, relativeHumidity REAL, temperature REAL,
            PM10 REAL, PM2P5 REAL, windDirection REAL, windSpeed REAL,
            windGust REAL, latitude REAL, longitude REAL,
            FOREIGN KEY(sensor_id) REFERENCES sensores(sensor_id),
            FOREIGN KEY(ficheiro_id) REFERENCES ficheiros(id) ON DELETE CASCADE,
            CHECK(timestamp_end_UTC > timestamp_init_UTC),
            UNIQUE(sensor_id, timestamp_init_UTC, timestamp_end_UTC)
        );
        CREATE INDEX IF NOT EXISTS idx_leituras_sensor_tempo
            ON leituras(sensor_id, timestamp_init_UTC);
        ''')
        # Deteta modelos antigos em vez de os apagar ou reinterpretar silenciosamente.
        colunas = {r['name'] for r in db.execute('PRAGMA table_info(leituras)')}
        if 'reading_id' not in colunas or 'timestamp_end_UTC' not in colunas:
            raise RuntimeError('Base de dados antiga detetada. Faz uma cópia e executa migrar_legado.py antes de iniciar.')


def listar_leituras(db, sensor=None):
    sql = '''SELECT l.*, s.nome AS sensor_nome,
             l.timestamp_init_Europe_Lisbon AS data,
             l.latitude AS lat, l.longitude AS lng,
             l.timestamp_init_UTC AS timestamp_init_UTC
             FROM leituras l JOIN sensores s ON s.sensor_id = l.sensor_id'''
    parametros = []
    if sensor is not None:
        sql += ' WHERE l.sensor_id = ?'
        parametros.append(sensor)
    sql += ' ORDER BY l.timestamp_init_UTC, l.reading_id'
    return [dict(r) for r in db.execute(sql, parametros)]
