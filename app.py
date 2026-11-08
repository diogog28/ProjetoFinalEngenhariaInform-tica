"""API REST Flask. Importa CSV por ETL e guarda tudo no SQLite."""
from pathlib import Path
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import ligar, inicializar, listar_leituras
from csv_parser import extrair_transformar, CAMPOS

app = Flask(__name__)
CORS(app, resources={r'/api/*': {'origins': ['http://localhost:5173', 'http://127.0.0.1:5173']}})
inicializar()


@app.get('/api/sensores')
def sensores():
    with ligar() as db:
        itens = [dict(r) for r in db.execute('SELECT sensor_id AS id, nome, latitude, longitude, timezone, installation_date, status FROM sensores ORDER BY sensor_id')]
    return jsonify(itens)


@app.get('/api/leituras')
def leituras():
    argumento = request.args.get('sensor', 'todos')
    if argumento != 'todos' and not argumento.isdecimal():
        return jsonify({'erro': 'sensor_id deve ser um número inteiro'}), 400
    with ligar() as db:
        resultado = listar_leituras(db, None if argumento == 'todos' else int(argumento))
    return jsonify(resultado)


@app.post('/api/upload')
def upload():
    ficheiros = request.files.getlist('ficheiros')
    if not ficheiros:
        return jsonify({'erro': 'Seleciona pelo menos um ficheiro CSV.'}), 400
    importados, ignorados, erros = [], [], []
    # Um ficheiro corresponde a um sensor/estação. O sensor_id é gerado pelo SQLite.
    # Para reutilizar sensor existente, enviar sensor_id inteiro no formulário.
    sensor_param = request.form.get('sensor_id', '').strip()
    if sensor_param and (not sensor_param.isdecimal() or int(sensor_param) < 1):
        return jsonify({'erro': 'sensor_id deve ser um inteiro positivo'}), 400
    for ficheiro in ficheiros:
        nome = Path(ficheiro.filename or '').name
        if not nome.lower().endswith('.csv'):
            erros.append(f'{nome}: extensão inválida')
            continue
        try:
            transformadas, rejeitadas = extrair_transformar(ficheiro)
            if not transformadas:
                raise ValueError('Nenhuma leitura válida')
            with ligar() as db:
                if db.execute('SELECT 1 FROM ficheiros WHERE nome=?', (nome,)).fetchone():
                    ignorados.append(nome)
                    continue
                if sensor_param:
                    sensor_id = int(sensor_param)
                    if not db.execute('SELECT 1 FROM sensores WHERE sensor_id=?', (sensor_id,)).fetchone():
                        raise ValueError('Sensor escolhido não existe')
                else:
                    nome_sensor = Path(nome).stem
                    reg = db.execute('SELECT sensor_id FROM sensores WHERE nome=?', (nome_sensor,)).fetchone()
                    if reg:
                        sensor_id = reg['sensor_id']
                    else:
                        primeira = next((r for r in transformadas if r['latitude'] is not None and r['longitude'] is not None), transformadas[0])
                        cur = db.execute('INSERT INTO sensores(nome, latitude, longitude) VALUES (?,?,?)',
                                         (nome_sensor, primeira['latitude'], primeira['longitude']))
                        sensor_id = cur.lastrowid
                fid = db.execute('INSERT INTO ficheiros(nome,sensor_id) VALUES (?,?)', (nome, sensor_id)).lastrowid
                colunas = ('sensor_id', 'ficheiro_id', *CAMPOS)
                campos_sql = ', '.join('"'+c+'"' for c in colunas)
                marcadores = ', '.join('?' for _ in colunas)
                db.executemany(f'INSERT INTO leituras ({campos_sql}) VALUES ({marcadores})',
                               [(sensor_id, fid, *[r[c] for c in CAMPOS]) for r in transformadas])
            importados.append({'nome': nome, 'sensor_id': sensor_id, 'leituras': len(transformadas), 'rejeitadas': rejeitadas[:20], 'total_rejeitadas': len(rejeitadas)})
        except (ValueError, UnicodeError, sqlite3.Error) as erro:
            erros.append(f'{nome}: {erro}')
    return jsonify({'importados': importados, 'ignorados': ignorados, 'erros': erros})


@app.delete('/api/dados')
def limpar():
    with ligar() as db:
        db.execute('DELETE FROM leituras')
        db.execute('DELETE FROM ficheiros')
        db.execute('DELETE FROM sensores')
    return jsonify({'mensagem': 'Dados eliminados.'})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
