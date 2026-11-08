<template>
  <section class="cyber-card p-3 mb-3">
    <div class="d-flex justify-content-between align-items-center gap-2 mb-2">
      <button class="btn btn-sm btn-outline-info" :disabled="modelValue <= 0" @click="$emit('update:modelValue', modelValue - 1)">Anterior</button>
      <div class="text-center"><div class="small text-info">NAVEGAÇÃO TEMPORAL</div><div class="small">{{ dataAtual }}</div></div>
      <button class="btn btn-sm btn-outline-info" :disabled="modelValue >= total - 1" @click="$emit('update:modelValue', modelValue + 1)">Seguinte</button>
    </div>
    <input class="form-range" type="range" min="0" :max="Math.max(0, total - 1)" :value="modelValue" @input="$emit('update:modelValue', Number($event.target.value))" />
    <div class="sparkline position-relative" v-if="pontos.length > 1">
      <svg width="100%" height="42" viewBox="0 0 1000 42" preserveAspectRatio="none" aria-label="Evolução de PM2.5">
        <polyline :points="pontosSvg" fill="none" stroke="#00e5ff" stroke-width="2" />
        <circle :cx="pontos[indiceSeguro]?.x" :cy="pontos[indiceSeguro]?.y" r="5" fill="#00ff88" stroke="white" stroke-width="2"/>
      </svg>
    </div>
    <div class="d-flex justify-content-between small text-secondary"><span>{{ primeiraData }}</span><span>{{ ultimaData }}</span></div>
  </section>
</template>
<script setup>
import { computed } from 'vue'
const props=defineProps({modelValue:{type:Number,default:0},total:{type:Number,default:0},leituras:{type:Array,default:()=>[]}})
defineEmits(['update:modelValue'])
function dataLegivel(valor) { if (!valor) return 'Sem data';const d=new Date(valor);return isNaN(d.getTime()) ? String(valor) : d.toLocaleString('pt-PT',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}) }
const dataAtual=computed(()=>dataLegivel(props.leituras[props.modelValue]?.data))
const primeiraData=computed(()=>dataLegivel(props.leituras[0]?.data))
const ultimaData=computed(()=>dataLegivel(props.leituras.at(-1)?.data))
const indiceSeguro=computed(()=>Math.max(0,Math.min(props.modelValue,pontos.value.length-1)))
const pontos=computed(()=>{
  // Os valores inválidos são excluídos da escala, sem os transformar em zero.
  const dados=props.leituras.map(l=>l.PM2P5 == null ? null : Number(l.PM2P5))
  const validos=dados.filter(n=>n!==null&&Number.isFinite(n))
  if (!validos.length) return []
  const min=Math.min(...validos), amplitude=Math.max(...validos)-min||1
  return dados.map((v,i)=>({x:(i/Math.max(1,dados.length-1))*1000,y:v===null||!Number.isFinite(v)?null:36-(v-min)/amplitude*30}))
})
const pontosSvg=computed(()=>pontos.value.map(p=>`${p.x},${p.y??36}`).join(' '))
</script>
