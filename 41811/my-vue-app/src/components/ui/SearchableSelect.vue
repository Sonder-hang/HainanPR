/**
 * 模糊搜索下拉选择组件
 * - 支持输入关键词过滤选项（模糊匹配 label）
 * - 自动显示序号
 * - 点击外部自动关闭
 */
<template>
  <div ref="containerRef" class="relative">
    <!-- 触发按钮（显示当前选中项） -->
    <button
      type="button"
      class="flex min-h-9 w-full cursor-pointer items-center justify-between rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-left text-[12px] text-[#1F264D] transition-colors hover:border-emerald-400 focus:border-emerald-400 focus:outline-none"
      :class="{ 'border-emerald-400': isOpen, 'rounded-b-none': isOpen }"
      @click="toggleOpen"
    >
      <span class="flex-1 truncate pr-2">
        {{ selectedLabel || placeholder }}
      </span>
      <span class="flex items-center gap-1.5">
        <span v-if="modelValue" class="rounded bg-[#e8eef9] px-1.5 py-0.5 text-[10px] font-medium text-[#596080]">
          已选 {{ selectedSeq }}
        </span>
        <svg
          class="h-3.5 w-3.5 flex-shrink-0 text-[#94a3b8] transition-transform"
          :class="isOpen ? 'rotate-180' : ''"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </span>
    </button>

    <!-- 搜索框（仅展开时显示） -->
    <div
      v-if="isOpen"
      class="absolute left-0 right-0 z-50 rounded-b-[2px] border border-t-0 border-[#b8c9e8]/60 bg-white shadow-md"
    >
      <div class="border-b border-[#e8eef9] px-2 py-1.5">
        <input
          ref="searchInputRef"
          v-model="searchKeyword"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full rounded-[2px] border border-[#b8c9e8]/60 bg-[#fafbff] px-2.5 py-1.5 text-[12px] text-[#1F264D] placeholder-[#94a3b8] focus:border-[#0A6EFD] focus:outline-none"
          @click.stop
        />
      </div>

      <!-- 选项列表 -->
      <ul class="max-h-60 overflow-y-auto">
        <li
          v-if="filteredOptions.length === 0"
          class="px-3 py-2.5 text-center text-[12px] text-[#94a3b8]"
        >
          无匹配结果
        </li>
        <li
          v-for="(opt, idx) in filteredOptions"
          :key="opt.value"
          class="flex cursor-pointer items-center px-3 py-2 text-[12px] transition-colors"
          :class="opt.value === modelValue
            ? 'bg-emerald-50 text-emerald-700'
            : 'text-[#1F264D] hover:bg-[#f0f4ff]'"
          @click="select(opt)"
        >
          <span class="mr-2 flex h-4 min-w-[20px] items-center justify-center rounded bg-[#e8eef9] px-1 text-[10px] font-medium text-[#596080]">
            {{ idx + 1 }}
          </span>
          <span class="flex-1 leading-snug">{{ opt.label }}</span>
          <span v-if="opt.value === modelValue" class="ml-2 text-[10px] text-[#0A6EFD]">✓</span>
        </li>
      </ul>

      <!-- 底部统计 -->
      <div v-if="filteredOptions.length > 0" class="border-t border-[#e8eef9] px-3 py-1.5 text-[10px] text-[#94a3b8]">
        共 {{ filteredOptions.length }} 项{{ searchKeyword ? '（已过滤）' : '' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

export interface SearchableOption {
  value: string | number
  label: string
  seq?: number
}

const props = withDefaults(defineProps<{
  modelValue: string | number
  options: SearchableOption[]
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
}>(), {
  placeholder: '请选择',
  searchPlaceholder: '输入关键词搜索…',
  emptyText: '无匹配结果',
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  change: [value: string | number]
}>()

const isOpen = ref(false)
const searchKeyword = ref('')
const containerRef = ref<HTMLElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

const selectedLabel = computed(() => {
  const found = props.options.find(o => String(o.value) === String(props.modelValue))
  return found?.label || ''
})

const selectedSeq = computed(() => {
  const idx = props.options.findIndex(o => String(o.value) === String(props.modelValue))
  return idx >= 0 ? idx + 1 : ''
})

const filteredOptions = computed(() => {
  if (!searchKeyword.value.trim()) return props.options
  const kw = searchKeyword.value.trim().toLowerCase()
  return props.options.filter(o => o.label.toLowerCase().includes(kw))
})

function toggleOpen() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchKeyword.value = ''
    nextTick(() => searchInputRef.value?.focus())
  }
}

function select(opt: SearchableOption) {
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
  isOpen.value = false
  searchKeyword.value = ''
}

// 外部点击关闭
function handleClickOutside(e: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    isOpen.value = false
    searchKeyword.value = ''
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))

// 重置搜索关键字当选项变化时
watch(() => props.options, () => {
  if (!isOpen.value) searchKeyword.value = ''
})
</script>
