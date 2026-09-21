import pandas as pd


def limpar_timestamps(
    df: pd.DataFrame, colunas: list, fuso_destino: str = 'Europe/Lisbon'
) -> pd.DataFrame:
    """Converte e limpa colunas de data/hora no formato ISO 8601 (com fuso horário),

    ajustando para a hora de Lisboa e tratando valores nulos.
    """
    for coluna in colunas:
        # 1. Converter texto ISO 8601 para DateTime
        df[coluna] = pd.to_datetime(df[coluna], utc=True, errors='coerce')

        # 2. Converter para a hora local de Lisboa
        df[coluna] = df[coluna].dt.tz_convert(fuso_destino)

        # 3. Remover a indicação do fuso (+01:00) para ficar limpo
        df[coluna] = df[coluna].dt.tz_localize(None)

        # 4. Preencher eventuais valores nulos com data padrão
        df[coluna] = df[coluna].fillna(pd.Timestamp('1970-01-01'))

    return df