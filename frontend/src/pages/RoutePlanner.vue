<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const out = ref(null)
const error = ref('')
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const run = async () => {
  error.value = ''
  out.value = null
  try {
    out.value = await postJSON('/api/quote', { start: start.value, end: end.value, persist: true })
  } catch (e) {
    error.value = String(e.message || e)
  }
}
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <p v-if="error" class="panel muted">试算失败：{{ error }}</p>
    <div v-if="out && out.reachable && out.allowed" class="panel">
      <p>站数 {{ out.hops }} · 换线 <strong>{{ out.transfers }}</strong> 次（上限 {{ out.max_transfers }} 次） · 票价 <span class="hero-num">¥{{ out.fare }}</span></p>
      <p class="muted">途经：{{ out.path.join(' → ') }}</p>
    </div>
    <div v-else-if="out && out.reachable && !out.allowed" class="panel">
      <p>⛔ {{ out.message }}</p>
      <p class="muted">实际换线 {{ out.transfers }} 次，允许上限 {{ out.max_transfers }} 次，整单拒绝，不予出票。</p>
      <p class="muted">途经：{{ out.path.join(' → ') }}</p>
    </div>
    <div v-else-if="out" class="panel">
      <p class="muted">不可达</p>
    </div>
  </div>
</template>
