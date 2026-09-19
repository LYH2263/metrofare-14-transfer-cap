<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const parseRow = (h) => {
  try { return { ...h, result: JSON.parse(h.result_json), input: JSON.parse(h.input_json) } }
  catch { return { ...h, result: null, input: null } }
}
onMounted(async () => { items.value = (await getJSON('/api/history')).items.map(parseRow) })
</script>
<template>
  <div class="page"><h1>试算记录</h1>
    <table>
      <tr><th>#</th><th>时间</th><th>起终</th><th>站数</th><th>换线次数（出票当时）</th><th>票价</th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td>
        <td>{{ h.created_at }}</td>
        <td>{{ h.input?.start }} → {{ h.input?.end }}</td>
        <td>{{ h.result?.hops ?? '—' }}</td>
        <td>{{ h.result?.transfers ?? '—' }}</td>
        <td>{{ h.result?.fare != null ? '¥' + h.result.fare : '—' }}</td>
      </tr>
    </table>
    <p class="muted">换线次数为出票当时快照，之后调整上限不会改写历史记录。</p>
  </div>
</template>
