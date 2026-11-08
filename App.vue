<template>
  <main class="container-fluid p-3 p-md-4 text-white">
    <TopHeader v-model="sensorSelecionado" :sensores="sensores" @upload="uploadFicheiro" />
    <button v-if="leituras.length" class="btn btn-outline-danger btn-sm mb-3" @click="limparDados">Limpar dados acumulados</button>
    <p v-if="erro" class="alert alert-danger">{{ erro }}</p>
    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
    <p v-if="!leiturasFiltradas.length" class="alert alert-warning">Importa ficheiros CSV para começar.</p>
    <template v-else>
      <TimeSlider v-model="indiceAtivo" :total="leiturasFiltradas.length" :leituras="leiturasFiltradas" />
      <WeatherMetrics :leitura="leituraAtual" />
      <div class="row g-3 mb-3">
        <div class="col-lg-3 d-flex flex-column gap-3">
          <AqiGaugeCard :aqi="aqiAtual" />
          <PollutantList :leitura="leituraAtual" />
        </div>
        <div class="col-lg-9"><AqiMap :sensores-dados="dadosMapa" /></div>
      </div>
      <div class="cyber-card p-3 mb-3">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6>EVOLUÇÃO HISTÓRICA</h6>
          <select v-model="poluenteSelecionado" class="form-select w-auto">
            <option v-for="p in poluentes" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <AqiEvolutionChart :dados-historicos="dadosGrafico" :poluente="poluenteSelecionado" />
      </div>
      <WeatherDetails :leitura="leituraAtual" />
    </template>
  </main>
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { airService } from './services/airService'
import { calcularAqiPm25 } from './services/aqi'
import TopHeader from './components/TopHeader.vue'
import TimeSlider from './components/TimeSlider.vue'
import WeatherMetrics from './components/WeatherMetrics.vue'
import WeatherDetails from './components/WeatherDetails.vue'
import AqiGaugeCard from './components/AqiGaugeCard.vue'
import PollutantList from './components/PollutantList.vue'
import AqiMap from './components/AqiMap.vue'
import AqiEvolutionChart from './components/AqiEvolutionChart.vue'

// Estado central: o backend é a fonte de verdade.
const leituras = ref([])
const sensores = ref([])
const sensorSelecionado = ref('todos')
const indiceAtivo = ref(0)
const poluenteSelecionado = ref('PM2P5')
const erro = ref('')
const sucesso = ref('')
const poluentes = ['PM2P5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']

async function carregarDados() {
  try {
    ;[sensores.value, leituras.value] = await Promise.all([airService.getSensores(), airService.getLeituras()])
  } catch { erro.value = 'Não foi possível contactar o servidor Flask.' }
}
onMounted(carregarDados)

// Filtro do sensor e leitura correspondente ao índice do slider.
const leiturasFiltradas = computed(() => sensorSelecionado.value === 'todos'
  ? leituras.value : leituras.value.filter(l => Number(l.sensor_id) === Number(sensorSelecionado.value)))
const leituraAtual = computed(() => leiturasFiltradas.value[indiceAtivo.value] || {})
watch(sensorSelecionado, () => { indiceAtivo.value = 0 })

// AQI PM2.5: apenas quando existem leituras suficientes para a média de 24 horas.
// Não se assume uma frequência fixa de amostragem.
function aqiNoInstante(sensorId, data) {
  const fim = Date.parse(data)
  if (!Number.isFinite(fim)) return null
  const inicio = fim - 24 * 60 * 60 * 1000
  const pontos = leituras.value.filter(l => l.sensor_id === sensorId && l.PM2P5 != null)
    .map(l => ({ t: Date.parse(l.data), v: l.PM2P5 }))
    .filter(l => Number.isFinite(l.t) && l.t > inicio && l.t <= fim)
    .sort((a, b) => a.t - b.t)
  // Regra conservadora de demonstração: 24 valores horários, cobrindo quase 24h.
  // Para dados sub-horários ou irregulares é necessária agregação temporal correta.
  if (pontos.length !== 24 || pontos.at(-1).t - pontos[0].t < 23 * 3600000) return null
  if (pontos.some((p, i) => i && p.t - pontos[i - 1].t !== 3600000)) return null
  return calcularAqiPm25(pontos.reduce((s, p) => s + p.v, 0) / pontos.length)
}
const aqiAtual = computed(() => {
  const l = leituraAtual.value
  return l.sensor_id ? aqiNoInstante(l.sensor_id, l.data) : null
})

const dadosGrafico = computed(() => leiturasFiltradas.value.map(l => ({
  x: l.data, y: l[poluenteSelecionado.value]
})))

// Para cada sensor, escolhe a leitura mais recente até ao instante selecionado.
const dadosMapa = computed(() => {
  const instante = Date.parse(leituraAtual.value.data)
  if (!Number.isFinite(instante)) return []
  return sensores.value.map(sensor => {
    const serie = leituras.value.filter(l => l.sensor_id === sensor.id && Date.parse(l.data) <= instante)
    const ultima = serie.at(-1)
    const coords = [...serie].reverse().find(l => Number.isFinite(l.lat) && Number.isFinite(l.lng))
    if (!ultima || !coords) return null
    return { id: sensor.id, lat: coords.lat, lng: coords.lng, aqi: aqiNoInstante(sensor.id, ultima.data) }
  }).filter(Boolean)
})

async function uploadFicheiro(event) {
  erro.value = ''; sucesso.value = ''
  const files = event.target.files
  if (!files?.length) return
  try {
    const r = await airService.uploadCSV(files)
    await carregarDados()
    sucesso.value = `${r.importados.length} ficheiro(s) importado(s).`
    if (r.erros.length || r.ignorados.length) erro.value = [...r.erros, ...r.ignorados.map(n => `${n}: já importado`)].join('; ')
  } catch (e) { erro.value = e.response?.data?.erro || 'Erro ao importar CSV.' }
  finally { event.target.value = '' }
}
async function limparDados() {
  if (!window.confirm('Eliminar todos os dados importados?')) return
  try {
    await airService.limparDados()
    sensorSelecionado.value = 'todos'; indiceAtivo.value = 0
    await carregarDados(); sucesso.value = 'Dados eliminados.'; erro.value = ''
  } catch { erro.value = 'Não foi possível eliminar os dados.' }
}
</script>
<style>
body { background: #08101a; color: white; font-family: system-ui, sans-serif; }
.cyber-card { background: linear-gradient(135deg,#0b1522,#101e2e); border:1px solid #1a2d42; border-radius:12px; }
h6 { color: #a3bcd7; font-size:.85rem; letter-spacing:1px; }
.form-select { background-color:#1e293b; color:#e2e8f0; border-color:#334155; }
</style>
