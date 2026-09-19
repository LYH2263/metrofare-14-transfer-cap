<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const parsed = (h) => { try { return JSON.parse(h.result_json) } catch { return {} } }
const inputOf = (h) => { try { return JSON.parse(h.input_json) } catch { return {} } }
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page"><h1>试算记录</h1>
    <table>
      <tr><th>#</th><th>起讫</th><th>站数</th><th>换线</th><th>票价</th><th>时间</th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td>
        <td>{{ inputOf(h).start }} → {{ inputOf(h).end }}</td>
        <td>{{ parsed(h).hops }}</td>
        <td>{{ parsed(h).transfers }} 次</td>
        <td>¥{{ parsed(h).fare }}</td>
        <td>{{ h.created_at }}</td>
      </tr>
    </table>
  </div>
</template>
