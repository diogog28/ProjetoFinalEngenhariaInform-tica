<template>
<section class="cyber-card p-3 text-center h-100">
  <h6>ÍNDICE DE QUALIDADE DO AR</h6>
  <svg viewBox="0 0 200 120" class="w-100" style="max-width:300px">
    <path d="M25 105 A75 75 0 0 1 175 105" fill="none" stroke="#25354b" stroke-width="20"/>
    <path d="M25 105 A75 75 0 0 1 175 105" fill="none" :stroke="cor" stroke-width="15" stroke-linecap="round" stroke-dasharray="235.6" :stroke-dashoffset="offset" style="transition:stroke-dashoffset .4s"/>
    <text x="100" y="95" :fill="cor" text-anchor="middle" font-size="30" font-weight="bold">{{ aqi ?? '--' }}</text>
    <text x="20" y="117" fill="#9ab4d0" font-size="9">0</text><text x="100" y="22" fill="#9ab4d0" font-size="9" text-anchor="middle">250</text><text x="170" y="117" fill="#9ab4d0" font-size="9">500</text>
  </svg>
  <p class="small text-secondary mb-0">{{ aqi == null ? 'AQI indisponível: são necessárias 24 leituras horárias válidas de PM2.5.' : 'AQI demonstrativo: PM2.5 (média de 24 h)' }}</p>
</section>
</template>
<script setup>
import { computed } from 'vue'
const props=defineProps({aqi:{type:Number,default:null}})
const offset=computed(()=>235.6*(1-Math.min(Math.max(props.aqi??0,0),500)/500))
const cor=computed(()=>props.aqi==null?'#64748b':props.aqi<=50?'#00e676':props.aqi<=100?'#ffea00':props.aqi<=150?'#ff7e00':props.aqi<=200?'#ff1744':'#b026ff')
</script>
