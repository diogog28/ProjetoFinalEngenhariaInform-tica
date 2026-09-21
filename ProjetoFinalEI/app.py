import json
import os
from flask import Flask, render_template, request, send_file
import pandas as pd
import plotly
import plotly.graph_objects as go

from ETLforDailyReadsV1Simple import limpar_timestamps

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extrair_valor_linha(df_linha, lista_nomes, padrao=0.0):
    for palavra in lista_nomes:
        for col in df_linha.index:
            if palavra.lower() in str(col).lower():
                val = df_linha[col]
                if pd.notnull(val):
                    try:
                        return round(float(val), 1)
                    except (ValueError, TypeError):
                        pass
    return padrao


@app.route('/', methods=['GET', 'POST'])
def index():
    erro = None
    download_ready = None
    dados_historicos = []
    poluentes_disponiveis = []

    filepath = None

    if request.method == 'POST':
        file = request.files.get('ficheiro')
        if file and file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

    if not filepath and os.path.exists('dados.csv'):
        filepath = 'dados.csv'

    if filepath:
        try:
            df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)

            colunas_ts = [
                'timestamp_init_Europe/Lisbon', 'timestamp_end_Europe/Lisbon',
                'timestamp_init_UTC', 'timestamp_end_UTC'
            ]
            cols_existentes = [c for c in colunas_ts if c in df.columns]

            if cols_existentes:
                df = limpar_timestamps(df, cols_existentes, fuso_destino='Europe/Lisbon')

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dados_limpos.csv')
            df.to_csv(output_path, index=False)
            download_ready = 'dados_limpos.csv'

            col_data = cols_existentes[0] if cols_existentes else df.columns[0]
            df[col_data] = pd.to_datetime(df[col_data], errors='coerce')
            df = df.dropna(subset=[col_data]).sort_values(by=col_data)

            # Mapeamento de colunas de poluentes/partículas presentes no dataset
            mapeamento_poluentes = {
                'PM2.5': ['pm2p5', 'pm2.5', 'pm2_5', 'pm25'],
                'PM10': ['pm10', 'pm_10'],
                'O₃': ['o3', 'ozone', 'ozono'],
                'NO₂': ['no2', 'nitrogen_dioxide'],
                'SO₂': ['so2', 'sulfur_dioxide'],
                'CO': ['co', 'carbon_monoxide']
            }

            for nome, keys in mapeamento_poluentes.items():
                for col in df.columns:
                    if any(k in col.lower() for k in keys):
                        poluentes_disponiveis.append(nome)
                        break

            # Converter cada linha para a estrutura JSON consumível pelo JavaScript
            for _, row in df.iterrows():
                pm25 = extrair_valor_linha(row, ['pm2p5', 'pm2.5', 'pm2_5', 'pm25'])
                pm10 = extrair_valor_linha(row, ['pm10', 'pm_10'])
                o3 = extrair_valor_linha(row, ['o3', 'ozone', 'ozono'])
                no2 = extrair_valor_linha(row, ['no2', 'nitrogen_dioxide'])
                so2 = extrair_valor_linha(row, ['so2', 'sulfur_dioxide'])
                co = extrair_valor_linha(row, ['co', 'carbon_monoxide'])

                temp = extrair_valor_linha(row, ['temperature', 'temp', 'temperatura'], 20.0)
                humidade = extrair_valor_linha(row, ['relativehumidity', 'humidity', 'humidade'], 50.0)
                pressao = extrair_valor_linha(row, ['pressure', 'pressao'], 1013.0)
                vento = extrair_valor_linha(row, ['windspeed', 'vento', 'wind'], 5.0)

                aqi = int(max(pm25 * 2.5, pm10 * 1.5, o3 * 0.8, 10))

                data_str = str(row[col_data])[:16].replace('T', ' ')

                dados_historicos.append({
                    'data': data_str,
                    'aqi': aqi,
                    'pm25': pm25, 'pm10': pm10, 'o3': o3,
                    'no2': no2, 'so2': so2, 'co': co,
                    'temp': temp, 'humidade': humidade,
                    'pressao': pressao, 'vento': vento
                })

        except Exception as e:
            erro = f'Erro ao processar o ficheiro: {str(e)}'

    return render_template(
        'index.html',
        erro=erro,
        download_ready=download_ready,
        dados_historicos_json=json.dumps(dados_historicos),
        poluentes=poluentes_disponiveis if poluentes_disponiveis else ['PM2.5', 'PM10', 'O₃', 'NO₂', 'SO₂', 'CO']
    )


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)