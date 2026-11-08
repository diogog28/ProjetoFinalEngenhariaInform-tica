<template>
  <div>
    <div style="height:340px"><Line v-if="dadosHistoricos.length" :data="dados" :options="opcoes" /><p v-else>Sem dados.</p></div>
    <div class="row row-cols-2 row-cols-md-5 g-2 mt-3">
      <div v-for="f in faixas" :key="f.nome" class="col">
        <div class="faixa p-2" :style="{'border-left-color':f.cor}">
          <div class="small fw-bold" :style="{color:f.cor}">{{ f.intervalo }}</div>
          <div class="small">{{ f.nome }}</div>
        </div>
      </div>
    </div>
    <p class="small text-secondary mt-2 mb-0">Faixas ilustrativas do AQI, não da concentração representada no gráfico.</p>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)
const props=defineProps({dadosHistoricos:{type:Array,default:()=>[]},poluente:{type:String,default:'PM2P5'}})
const faixas=[{intervalo:'0–50',nome:'BOA',cor:'#00ff88'},{intervalo:'51–100',nome:'MODERADA',cor:'#ffb700'},{intervalo:'101–150',nome:'SENSÍVEIS',cor:'#ff7b00'},{intervalo:'151–200',nome:'INSALUBRE',cor:'#ff4d4d'},{intervalo:'201+',nome:'MUITO INSALUBRE',cor:'#b026ff'}]
function dataLegivel(valor){const d=new Date(valor);return isNaN(d.getTime())?String(valor??''):d.toLocaleDateString('pt-PT',{day:'2-digit',month:'short',year:'2-digit'})}
const dados=computed(()=>({labels:props.dadosHistoricos.map(p=>dataLegivel(p.x)),datasets:[{label:props.poluente,data:props.dadosHistoricos.map(p=>p.y),borderColor:'#00e5ff',backgroundColor:'rgba(0,229,255,.12)',pointRadius:2,pointHoverRadius:5,borderWidth:2,tension:.25,fill:true,spanGaps:false}]}))
const opcoes=computed(()=>({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`${props.poluente}: ${ctx.parsed.y} ${props.poluente==='CO'?'mg/m³':'µg/m³'}`}}},scales:{x:{ticks:{maxTicksLimit:8,color:'#9ab4d0',maxRotation:0}},y:{beginAtZero:true,ticks:{color:'#9ab4d0'},grid:{color:'rgba(255,255,255,.05)'}}}}))
</script>
<style scoped>.faixa{background:#111d2e;border:1px solid #2b394a;border-left:3px solid;border-radius:5px;min-height:56px}</style>
