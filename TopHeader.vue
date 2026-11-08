<template>
  <header class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
    <h3 class="m-0 text-info">AQI DASHBOARD</h3>
    <div class="d-flex gap-2 align-items-center">
      <label for="sensor">Sensor:</label>
      <select id="sensor" class="form-select" :value="modelValue" @change="$emit('update:modelValue', $event.target.value === 'todos' ? 'todos' : Number($event.target.value))">
        <option value="todos">Todos os sensores</option>
        <option v-for="sensor in sensores" :key="sensor.id" :value="sensor.id">{{ sensor.nome }}</option>
      </select>
      <label class="btn btn-outline-info text-nowrap">Importar CSV
        <input type="file" accept=".csv" multiple hidden @change="$emit('upload', $event)" />
      </label>
    </div>
  </header>
</template>
<script setup>
defineProps({ sensores: { type: Array, default: () => [] }, modelValue: { type: [String, Number], default: 'todos' } })
defineEmits(['update:modelValue', 'upload'])
</script>
