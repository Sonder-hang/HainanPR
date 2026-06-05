<template>
  <div class="relative">
    <button
      type="button"
      class="flex min-h-9 flex-wrap items-center justify-between rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] outline-none focus:border-emerald-400"
      style="width: 200px;"
      @click="isOpen = !isOpen"
    >
      <span class="flex-1 truncate-multiline">{{ displayText }}</span>
      <svg
        class="h-4 w-4 flex-shrink-0 text-[#9CA3AF] transition-transform"
        :class="isOpen ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="absolute z-10 mt-2 rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-md"
      style="width: 200px;"
    >
      <!-- 搜索框 -->
      <div class="border-b border-[#E5E7EB] p-2">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索医院..."
            class="w-full rounded border border-[#D1D5DB] bg-white px-3 py-1.5 pl-8 text-[12px] text-[#374151] outline-none focus:border-emerald-400"
            @click.stop
          />
          <svg
            class="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#9CA3AF]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <button
            v-if="searchQuery"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#374151]"
            @click.stop="searchQuery = ''"
          >
            <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 选项列表 -->
      <div class="max-h-52 overflow-y-auto py-1">
        <div v-if="filteredOptions.length === 0" class="px-3 py-3 text-center text-[13px] text-[#9CA3AF]">
          未找到匹配结果
        </div>
        <div
          v-for="option in filteredOptions"
          v-else
          :key="option.value"
          class="flex items-center px-3 py-2 text-[12px] text-[#374151] hover:bg-[#F3F4F6] cursor-pointer"
          @click="toggleOption(option.value)"
        >
          <input
            type="checkbox"
            :checked="modelValue.includes(option.value)"
            class="mr-2 h-4 w-4 accent-[#2E57E5]"
          />
          <span>{{ option.label }}</span>
        </div>
      </div>

      <!-- 已选数量提示 -->
      <div v-if="modelValue.length > 0" class="border-t border-[#E5E7EB] px-3 py-1.5 text-[12px] text-[#9CA3AF]">
        已选 {{ modelValue.length }} 项
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

interface Option {
  value: string
  label: string
}

const props = defineProps<{
  modelValue: string[]
  options: Option[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const isOpen = ref(false)
const searchQuery = ref('')

const filteredOptions = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.options
  }
  const q = searchQuery.value.trim().toLowerCase()
  return props.options.filter(opt => opt.label.toLowerCase().includes(q))
})

const displayText = computed(() => {
  if (props.modelValue.length === 0) {
    return props.placeholder || '请选择'
  }
  const selectedLabels = props.modelValue.map(value => {
    const option = props.options.find(opt => opt.value === value)
    return option?.label || ''
  }).filter(Boolean)
  return selectedLabels.join('、')
})

const toggleOption = (value: string) => {
  const currentIndex = props.modelValue.indexOf(value)
  let newValues: string[]

  if (currentIndex > -1) {
    newValues = [...props.modelValue]
    newValues.splice(currentIndex, 1)
  } else {
    newValues = [...props.modelValue, value]
  }

  emit('update:modelValue', newValues)
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    isOpen.value = false
    searchQuery.value = ''
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('click', handleClickOutside)
}

const cleanup = () => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('click', handleClickOutside)
  }
}

onUnmounted(cleanup)
</script>

<style scoped>
.truncate-multiline {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
