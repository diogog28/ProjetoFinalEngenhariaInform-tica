// Exemplo simplificado: AQI dos EUA baseado em PM2.5 (média de 24h).
// Os pontos de corte devem ser confirmados para a norma/ano usados no relatório.
// Não aplicar este cálculo diretamente a leituras instantâneas.
const faixas = [
  [0, 9, 0, 50], [9.1, 35.4, 51, 100], [35.5, 55.4, 101, 150],
  [55.5, 125.4, 151, 200], [125.5, 225.4, 201, 300], [225.5, 325.4, 301, 500]
]
export function calcularAqiPm25(media24h) {
  if (media24h == null || !Number.isFinite(Number(media24h)) || media24h < 0) return null
  const c = Math.floor(Number(media24h) * 10) / 10
  const faixa = faixas.find(([min, max]) => c >= min && c <= max)
  if (!faixa) return null
  const [cMin, cMax, iMin, iMax] = faixa
  return Math.round(((iMax - iMin) / (cMax - cMin)) * (c - cMin) + iMin)
}
