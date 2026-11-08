"""ETL: Extract -> Transform -> Load (a inserção SQL é feita em app.py).

Extract: abrir CSV UTF-8 BOM, detetar separador, ler os 19 campos.
Transform: converter números, datas ISO, validar intervalos, remover
registos incompletos/duplicados; valores em falta são NULL, nunca zero.
Load: função de inserção transacional no backend, com FK para sensor.
"""
import csv
import io
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NUMERICOS = ('NO2', 'O3', 'CO', 'SO2', 'PM1', 'pressure', 'relativeHumidity',
            'temperature', 'PM10', 'PM2P5', 'windDirection', 'windSpeed',
            'windGust', 'latitude', 'longitude')
TIMESTAMPS = ('timestamp_init_UTC', 'timestamp_end_UTC',
              'timestamp_init_Europe_Lisbon', 'timestamp_end_Europe_Lisbon')
CAMPOS = (*TIMESTAMPS, *NUMERICOS)
ALIASES = {
    'no2': 'NO2', 'o3': 'O3', 'co': 'CO', 'so2': 'SO2', 'pm1': 'PM1',
    'pressure': 'pressure', 'relativehumidity': 'relativeHumidity',
    'temperature': 'temperature', 'pm10': 'PM10', 'pm2p5': 'PM2P5',
    'winddirection': 'windDirection', 'windspeed': 'windSpeed',
    'windgust': 'windGust', 'latitude': 'latitude', 'longitude': 'longitude',
    'timestamp_init_utc': 'timestamp_init_UTC',
    'timestamp_end_utc': 'timestamp_end_UTC',
    'timestamp_init_europe/lisbon': 'timestamp_init_Europe_Lisbon',
    'timestamp_end_europe/lisbon': 'timestamp_end_Europe_Lisbon',
}


def normalizar_cabecalho(nome):
    # Ex.: "NO2(µg/m³)" -> "no2"; evita confundir PM1 e PM10.
    return nome.strip().split('(')[0].strip().lower()


def numero(valor):
    if valor is None or not str(valor).strip():
        return None
    n = float(str(valor).strip().replace(',', '.'))
    if not math.isfinite(n):
        raise ValueError('Número não finito')
    return n


def data_iso(valor):
    if not valor or not str(valor).strip():
        return None
    data = datetime.fromisoformat(str(valor).strip().replace('Z', '+00:00'))
    if data.tzinfo is None:
        raise ValueError('Timestamp sem fuso horário')
    return data


def extrair_transformar(ficheiro):
    conteudo = ficheiro.read().decode('utf-8-sig')
    try:
        separador = csv.Sniffer().sniff(conteudo[:4096], delimiters=',;').delimiter
    except csv.Error:
        separador = ','
    leitor = csv.DictReader(io.StringIO(conteudo), delimiter=separador)
    if not leitor.fieldnames:
        raise ValueError('CSV sem cabeçalho')
    mapeamento = {col: ALIASES[normalizar_cabecalho(col)]
                  for col in leitor.fieldnames if col and normalizar_cabecalho(col) in ALIASES}
    # Só timestamps UTC são indispensáveis; os de Lisboa podem ser reconstruídos.
    essenciais = {'timestamp_init_UTC', 'timestamp_end_UTC'}
    if not essenciais.issubset(set(mapeamento.values())):
        raise ValueError('Faltam timestamp_init_UTC ou timestamp_end_UTC')

    leituras, rejeitadas, vistos = [], [], set()
    for linha_n, linha in enumerate(leitor, start=2):
        if not any(v and str(v).strip() for v in linha.values()):
            continue
        try:
            bruto = {mapeamento[k]: v for k, v in linha.items() if k in mapeamento}
            inicio = data_iso(bruto.get('timestamp_init_UTC'))
            fim = data_iso(bruto.get('timestamp_end_UTC'))
            if inicio is None or fim is None or fim <= inicio:
                raise ValueError('Intervalo UTC inválido')
            # Canonização em UTC permite ordenação lexical segura no SQLite.
            reg = {
                'timestamp_init_UTC': inicio.astimezone(timezone.utc).isoformat(timespec='milliseconds'),
                'timestamp_end_UTC': fim.astimezone(timezone.utc).isoformat(timespec='milliseconds')
            }
            zona = ZoneInfo('Europe/Lisbon')
            for chave, instante in [('timestamp_init_Europe_Lisbon', inicio),
                                   ('timestamp_end_Europe_Lisbon', fim)]:
                informado = data_iso(bruto.get(chave))
                if informado and abs((informado - instante).total_seconds()) > 1:
                    raise ValueError(f'{chave} incoerente com UTC')
                reg[chave] = instante.astimezone(zona).isoformat(timespec='milliseconds')
            for campo in NUMERICOS:
                reg[campo] = numero(bruto.get(campo))
            if reg['latitude'] is not None and not -90 <= reg['latitude'] <= 90:
                raise ValueError('Latitude fora do intervalo')
            if reg['longitude'] is not None and not -180 <= reg['longitude'] <= 180:
                raise ValueError('Longitude fora do intervalo')
            if reg['relativeHumidity'] is not None and not 0 <= reg['relativeHumidity'] <= 100:
                raise ValueError('Humidade fora do intervalo')
            for campo in ('NO2', 'O3', 'CO', 'SO2', 'PM1', 'PM10', 'PM2P5', 'windSpeed', 'windGust'):
                if reg[campo] is not None and reg[campo] < 0:
                    raise ValueError(f'{campo} negativo')
            chave = (reg['timestamp_init_UTC'], reg['timestamp_end_UTC'])
            if chave in vistos:
                raise ValueError('Intervalo duplicado no mesmo ficheiro')
            vistos.add(chave)
            leituras.append(reg)
        except (ValueError, TypeError) as erro:
            rejeitadas.append({'linha': linha_n, 'motivo': str(erro)})
    return leituras, rejeitadas
