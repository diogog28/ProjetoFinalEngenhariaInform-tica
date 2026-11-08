<template>
  <section class="cyber-card p-3 h-100">
    <h6 class="mb-3">POLUENTES E VALORES DE REFERÊNCIA</h6>
    <div v-for="pol in poluentes" :key="pol.id" class="mb-3">
      <div class="d-flex justify-content-between align-items-center gap-2">
        <span class="text-info fw-semibold small">{{ pol.nome }}</span>
        <span class="small text-light">{{ formatar(leitura[pol.id], pol.id) }} {{ pol.unidade }}</span>
      </div>
      <div class="progress mt-2" style="height:7px;background:#263448">
        <div class="progress-bar" :class="corBarra(pol)" :style="{width: percentagem(pol) + '%'}"></div>
      </div>
      <div class="d-flex justify-content-between mt-1 text-secondary legenda-pequena">
        <span>{{ pol.tipo }}</span><span>{{ pol.referencia }} {{ pol.unidade }}</span>
      </div>
    </div>
    <p class="small text-secondary mb-0">As barras indicam apenas a proporção da leitura face a um valor de referência histórico; <strong>não indicam incumprimento legal</strong>. A verificação exige médias e regras temporais adequadas e legislação atualizada.</p>
  </section>
</template>
<script setup>
// Mantêm-se os valores históricos ilustrativos da versão anterior.
// Não são usados para declarar infrações legais.
const props = defineProps({ leitura: { type: Object, default: () => ({}) } })
const poluentes = [
  { id:'PM2P5', nome:'Partículas PM2.5', referencia:25, unidade:'µg/m³', tipo:'Referência anual histórica' },
  { id:'PM10', nome:'Partículas PM10', referencia:50, unidade:'µg/m³', tipo:'Referência diária histórica' },
  { id:'NO2', nome:'Dióxido de azoto (NO₂)', referencia:200, unidade:'µg/m³', tipo:'Referência horária histórica' },
  { id:'O3', nome:'Ozono (O₃)', referencia:180, unidade:'µg/m³', tipo:'Limiar horário de informação' },
  { id:'SO2', nome:'Dióxido de enxofre (SO₂)', referencia:350, unidade:'µg/m³', tipo:'Referência horária histórica' },
  { id:'CO', nome:'Monóxido de carbono (CO)', referencia:10, unidade:'mg/m³', tipo:'Referência de média de 8 horas' }
]
function formatar(valor,id) { return valor == null || !Number.isFinite(Number(valor)) ? 'N/D' : Number(valor).toFixed(id === 'CO' ? 3 : 1) }
function percentagem(pol) { const n = Number(props.leitura[pol.id]); return props.leitura[pol.id] == null || !Number.isFinite(n) ? 0 : Math.max(0,Math.min(100,n / pol.referencia * 100)) }
function corBarra(pol) { const p=percentagem(pol);return p>90?'bg-danger':p>70?'bg-warning':'bg-info' }
</script>
<style scoped>.legenda-pequena{font-size:.68rem}</style>
