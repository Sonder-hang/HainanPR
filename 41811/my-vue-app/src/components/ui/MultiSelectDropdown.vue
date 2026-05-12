<template>
  <div class="relative">
    <button
      type="button"
      class="flex min-h-8 w-[300px] flex-wrap items-center justify-between rounded border border-[#D1D5DB] bg-white px-3 py-2 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5]"
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
      class="absolute z-10 mt-2 w-[300px] max-h-64 overflow-y-auto rounded border border-[#D1D5DB] bg-white shadow-md"
    >
      <div
        v-for="option in options"
        :key="option.value"
        class="flex items-center px-3 py-2 text-[14px] text-[#374151] hover:bg-[#F3F4F6] cursor-pointer"
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
