<template>
  <div class="animate-fade-in space-y-6">
    <div class="rounded border border-[#E5E7EB] bg-white p-7 text-[#4B5563] shadow-sm">
      <h3 class="mb-2 text-[18px] font-bold text-[#1F2937]">{{ title }}</h3>
      <p class="text-[14px] leading-relaxed">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const title = computed(() => (route.meta.title as string) ?? '模块')
const description = computed(
  () =>
    (route.meta.description as string) ??
    '该模块页面建设中。',
)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-in-out;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
