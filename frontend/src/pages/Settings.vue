<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const maxTransfers = ref(0)
const saved = ref(false)
const error = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  maxTransfers.value = s.value.max_transfers ?? 1
})
const save = async () => {
  error.value = ''
  saved.value = false
  try {
    s.value = await putJSON('/api/settings', { max_transfers: Number(maxTransfers.value) })
    maxTransfers.value = s.value.max_transfers
    saved.value = true
  } catch (e) {
    error.value = String(e.message || e)
  }
}
</script>
<template>
  <div class="page"><h1>设置</h1>
    <div class="panel">
      <label>
        允许的最大换线次数
        <input v-model.number="maxTransfers" type="number" min="0" step="1" />
      </label>
      <button @click="save">保存</button>
      <p v-if="saved" class="muted">已保存，后续询价按新上限判定。</p>
      <p v-if="error" class="muted">保存失败：{{ error }}</p>
      <p class="muted">当前上限：{{ s.max_transfers }} 次</p>
    </div>
    <pre>{{ s }}</pre>
  </div>
</template>
