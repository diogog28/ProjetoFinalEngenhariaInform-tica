<template>
  <section class="cyber-card p-3"><h6>METEOROLOGIA E SENSOR</h6>
    <p class="mb-1">Rajada: {{ leitura.windGust ?? 'N/D' }} m/s · Direção: {{ leitura.windDirection ?? 'N/D' }}°</p>
    <p class="mb-1">Sensor: {{ leitura.sensor_id ?? 'N/D' }}</p>
    <p class="mb-0">Data: {{ leitura.data ?? 'N/D' }}</p>
  </section>
</template>
<script setup>
defineProps({ leitura: { type: Object, default: () => ({}) } })
</script>
