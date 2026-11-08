<template>
  <div class="row g-3 mb-3">
    <div v-for="item in itens" :key="item.chave" class="col-6 col-lg-3"><div class="cyber-card p-3">
      <div class="small text-secondary">{{ item.nome }}</div><strong>{{ leitura[item.chave] == null ? 'N/D' : Number(leitura[item.chave]).toFixed(1) }} {{ item.unidade }}</strong>
    </div></div>
  </div>
</template>
<script setup>
defineProps({ leitura: { type: Object, default: () => ({}) } })
const itens = [
  { chave: 'temperature', nome: 'Temperatura', unidade: '°C' },
  { chave: 'relativeHumidity', nome: 'Humidade', unidade: '%' },
  { chave: 'windSpeed', nome: 'Vento', unidade: 'm/s' },
  { chave: 'pressure', nome: 'Pressão', unidade: 'hPa' }
]
</script>
