# Qualidade do Ar — Vue + Flask + SQLite com ETL

Projeto derivado da versão **visual melhorada**. Mantém os componentes Vue e substitui o armazenamento pelo esquema relacional `sensores` (1) → (N) `leituras`.

## 1. Arrancar em Windows / VS Code (raiz do ZIP)

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm install
backend\.venv\Scripts\Activate.ps1
npm run dev
```

O `npm run dev` inicia Vite e Flask simultaneamente. Frontend: http://127.0.0.1:5173; API: http://localhost:5000/api.

## 2. Base de dados

- `sensores`: `sensor_id INTEGER PRIMARY KEY`, nome, latitude, longitude, fuso horário, data de instalação, estado.
- `leituras`: `reading_id INTEGER PRIMARY KEY`, `sensor_id INTEGER NOT NULL` (FK), `ficheiro_id`, quatro timestamps, 15 campos numéricos (13 medições + latitude + longitude). Guarda todos os **19 campos** do CSV, para além das chaves.
- `ficheiros`: nomes importados, sensor_id e data de importação, para impedir repetir o mesmo ficheiro.
- Os aliases `data`, `lat`, `lng` são devolvidos **pela API**, não duplicados na tabela SQLite, para manter os componentes Vue existentes.
- Os IDs de sensor são gerados automaticamente como **inteiros** a partir do nome do ficheiro sem `.csv` (ex.: `BET0024J028`), ou podem ser explicitamente fornecidos como inteiro no campo multipart `sensor_id`. O nome amigável não substitui o ID numérico.

## 3. ETL explicado

1. **Extract** (`csv_parser.py`): descodificar UTF-8 (com ou sem BOM), detetar vírgula/ponto e vírgula, ler linhas CSV.
2. **Transform** (`csv_parser.py`): mapear cabeçalhos `NO2(µg/m³)` → `NO2`, `PM2P5(µg/m³)` → `PM2P5`, validar datas com fuso, converter números, validar lat/lon/humidade e valores negativos, deduplicar intervalos repetidos dentro do ficheiro. Linhas inválidas ficam no resumo `rejeitadas`; medições vazias tornam-se `NULL`, não zero. Timestamps de Lisboa são também recalculados a partir dos timestamps UTC com `Europe/Lisbon` para aplicar horário de verão corretamente.
3. **Load** (`app.py` + `database.py`): transação SQLite cria/consulta sensor, regista ficheiro, insere cada leitura com `sensor_id` numérico e integridade referencial. Um erro de unicidade ou SQL reverte a importação desse ficheiro.

**Unidades**: `pressure(µg/m³)` no CSV é uma indicação inconsistente com valores como `984.5`, que tipicamente seriam hPa. O ETL **não converte** nem assume unidades: armazena o valor exatamente como foi recebido. Confirmar a unidade com a fonte dos dados antes de publicar o relatório.

## 4. Migração dos dados antigos

O `qualidade_ar.db` anterior tinha `sensor_id TEXT` e não preservava todos os timestamps. **Não o substituas sem fazer cópia.** Como não se podem reconstruir com segurança as horas finais ausentes, a migração recomendada é:

1. Parar o servidor Flask.
2. Fazer backup de `backend/qualidade_ar.db` antigo (por exemplo `qualidade_ar-antigo.db`).
3. Retirar o ficheiro SQLite antigo da pasta `backend` do novo projeto.
4. Iniciar o projeto; o novo esquema é criado automaticamente.
5. Importar novamente os CSV originais. Cada ficheiro passa pelo ETL e obtém um `sensor_id INTEGER`.

A aplicação deteta esquemas antigos e recusa-se a sobrescrevê-los silenciosamente.

## 5. Verificação rápida

```powershell
cd backend
python -m unittest test_etl.py
```

**Importante:** O cálculo demonstrativo do AQI presente no frontend exige leituras horárias suficientes; dados diários não devem ser usados como se fossem horários. Valores de limites legais requerem agregação temporal por poluente.
