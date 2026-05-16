<template>
  <div
    ref="containerRef"
    class="overflow-y-auto"
    :style="{ maxHeight: maxHeight }"
    @scroll="onScroll"
  >
    <!-- 占位高度，撑起滚动条 -->
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <!-- 渲染可见行 -->
      <table
        class="w-full min-w-[500px] border-collapse text-left text-[11px]"
        :style="{ position: 'absolute', top: offsetY + 'px', left: 0, width: '100%' }"
      >
        <thead class="border-b border-[#b8c9e8]/60 bg-[#f0f4ff]">
          <tr>
            <th
              v-for="col in columns"
              :key="col"
              class="px-3 py-2 font-semibold text-[#596080]"
            >{{ col }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#b8c9e8]/30">
          <tr
            v-for="(row, idx) in visibleRows"
            :key="startIndex + idx"
            class="hover:bg-emerald-50/30"
          >
            <td
              v-for="col in columns"
              :key="col"
              class="max-w-[200px] truncate px-3 py-2 text-[#334155]"
              :title="String(row[col] ?? '—')"
            >{{ row[col] ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface Props {
  columns: string[]
  rows: Record<string, unknown>[]
  rowHeight?: number
  overscan?: number
  maxHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  rowHeight: 36,
  overscan: 5,
  maxHeight: '300px',
})

const containerRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)
const viewportHeight = ref(600)

const totalHeight = computed(() => props.rows.length * props.rowHeight)

const startIndex = computed(() => {
  const raw = Math.floor(scrollTop.value / props.rowHeight) - props.overscan
  return Math.max(0, raw)
})

const visibleCount = computed(() => {
  return Math.ceil(viewportHeight.value / props.rowHeight) + props.overscan * 2
})

const endIndex = computed(() => {
  return Math.min(props.rows.length, startIndex.value + visibleCount.value)
})

const visibleRows = computed(() => {
  return props.rows.slice(startIndex.value, endIndex.value)
})

const offsetY = computed(() => startIndex.value * props.rowHeight)

let rafId: number | null = null

function onScroll() {
  if (rafId !== null) return
  rafId = requestAnimationFrame(() => {
    if (containerRef.value) {
      scrollTop.value = containerRef.value.scrollTop
    }
    rafId = null
  })
}

function updateViewport() {
  if (containerRef.value) {
    viewportHeight.value = containerRef.value.clientHeight
  }
}

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
  }
})
</script>
