"""Testes simples: executa `python -m unittest test_etl.py` na pasta backend."""
import io
import os
import tempfile
import unittest
from pathlib import Path
from csv_parser import extrair_transformar

CABECALHO = ('timestamp_init_UTC,timestamp_end_UTC,timestamp_init_Europe/Lisbon,'
             'timestamp_end_Europe/Lisbon,NO2(µg/m³),O3(µg/m³),CO(mg/m³),'
             'SO2(µg/m³),PM1(µg/m³),pressure(µg/m³),relativeHumidity(%),'
             'temperature(C),PM10(µg/m³),PM2P5(µg/m³),windDirection(degrees),'
             'windSpeed(m/s),windGust(m/s),latitude,longitude\n')
LINHA = ('2025-03-01T00:00:00.000Z,2025-03-02T00:00:00.000Z,'
         '2025-03-01T00:00:00.000+00:00,2025-03-02T00:00:00.000+00:00,'
         '19.5,30.5,0.042,2.6,8,984.5,78.7,13.41,18,8,4.886220851983609,'
         '1.2,3.6,38.0126,-7.85931\n')

class TestETL(unittest.TestCase):
    def test_exemplo(self):
        dados, erros = extrair_transformar(io.BytesIO((CABECALHO+LINHA).encode()))
        self.assertEqual(len(dados), 1)
        self.assertEqual(erros, [])
        self.assertEqual(dados[0]['CO'], 0.042)
        self.assertEqual(dados[0]['PM2P5'], 8)
        self.assertEqual(dados[0]['pressure'], 984.5)
        self.assertEqual(dados[0]['timestamp_end_UTC'], '2025-03-02T00:00:00.000+00:00')
    def test_intervalo_duplicado(self):
        dados, erros = extrair_transformar(io.BytesIO((CABECALHO+LINHA+LINHA).encode()))
        self.assertEqual(len(dados), 1)
        self.assertEqual(len(erros), 1)

if __name__ == '__main__':
    unittest.main()
