<template><section class="cyber-card p-3 h-100"><h6>MAPA DE QUALIDADE DO AR</h6><div ref="mapElement" style="height:400px;border-radius:8px;z-index:0"></div></section></template>
<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
const props = defineProps({ sensoresDados: { type: Array, default: () => [] } })
const mapElement = ref(null)
let map, camada
function cor(aqi) {
  if (aqi == null) return '#64748b'
  return aqi <= 50 ? '#00e400' : aqi <= 100 ? '#ffff00' : aqi <= 150 ? '#ff7e00' : aqi <= 200 ? '#ff0000' : '#8f3f97'
}
function desenhar() {
  if (!map) return
  camada.clearLayers()
  for (const sensor of props.sensoresDados) {
    if (!Number.isFinite(sensor.lat) || !Number.isFinite(sensor.lng)) continue
    // Popup composto com texto (sem interpolação HTML não confiável).
    const conteudo = document.createElement('div')
    conteudo.textContent = `${sensor.id} · AQI: ${sensor.aqi ?? 'N/D'}`
    L.circleMarker([sensor.lat, sensor.lng], { radius: 12, color: '#fff', weight: 2, fillColor: cor(sensor.aqi), fillOpacity: .85 })
      .bindPopup(conteudo).addTo(camada)
  }
  if (camada.getLayers().length) map.fitBounds(camada.getBounds(), { padding: [30, 30], maxZoom: 14 })
}
onMounted(async () => {
  map = L.map(mapElement.value).setView([38.0151, -7.8632], 12)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }).addTo(map)
  camada = L.featureGroup().addTo(map)
  await nextTick(); map.invalidateSize(); desenhar()
})
watch(() => props.sensoresDados, desenhar, { deep: true })
onBeforeUnmount(() => { map?.remove(); map = null })
</script>
