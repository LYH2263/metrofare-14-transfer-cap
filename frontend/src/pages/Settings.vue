<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const maxTransfers = ref(0)
const msg = ref('')
const load = async () => {
  s.value = await getJSON('/api/settings')
  maxTransfers.value = Number(s.value.max_transfers ?? 0)
}
const save = async () => {
  s.value = await putJSON('/api/settings', { max_transfers: Number(maxTransfers.value) })
  msg.value = '已保存'
  setTimeout(() => { msg.value = '' }, 2000)
}
onMounted(load)
</script>
<template>
  <div class="page"><h1>设置</h1>
    <div class="panel">
      <label>最大换线次数
        <input type="number" min="0" step="1" v-model="maxTransfers" />
      </label>
      <button @click="save">保存</button>
      <span v-if="msg" class="muted"> {{ msg }}</span>
    </div>
    <div class="panel"><pre>{{ s }}</pre></div>
  </div>
</template>
