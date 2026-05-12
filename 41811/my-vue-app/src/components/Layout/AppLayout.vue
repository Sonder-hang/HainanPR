<template>
  <div class="flex h-screen flex-col overflow-hidden bg-white font-sans text-[#1a1a1a]">
    <!-- 顶部导航栏 -->
    <header class="flex h-[88px] shrink-0 flex-col border-b border-[#b8c9e8]/60 shadow-[0_1px_3px_rgba(0,0,0,0.06)]">
      <div class="flex h-[88px] shrink-0 items-center justify-between bg-[#cbd9f4] px-6">
        <div class="flex items-center">
          <div
            class="flex h-[52px] items-center bg-white px-4 text-[15px] font-semibold tracking-[0.35em] text-[#111827] shadow-sm"
            style="margin-left: 24px;"
          >
            三医联动监管与评价
          </div>
        </div>
        <div class="flex items-center gap-10 text-[#1e3a5f]">
          <RouterLink
            to="/dashboard"
            class="flex flex-col items-center gap-0.5 transition-opacity hover:opacity-80"
          >
            <Home :size="20" class="text-[#2563eb]" stroke-width="2" />
            <span class="text-[12px] leading-tight text-[#0f172a]">返回首页</span>
          </RouterLink>
          <div class="flex flex-col items-center gap-0.5">
            <ShieldAlert :size="20" class="text-[#0A6EFD]" stroke-width="2" />
            <span class="text-[12px] leading-tight text-[#0f172a]">admin</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主体内容区 -->
    <div class="flex min-h-0 flex-1">
      <!-- 左侧导航栏 -->
      <aside
        class="relative z-20 flex w-[240px] shrink-0 flex-col border-r border-[#b8c9e8]/50 bg-[#d3e2fd] text-[#334155] shadow-[inset_-1px_0_0_rgba(255,255,255,0.35)]"
      >
        <div class="flex-1 overflow-y-auto py-5">
          <div class="mb-2 px-5 text-[11px] font-bold uppercase tracking-wider text-[#5b6b8c]">
            四要素页面设计
          </div>
          <nav class="space-y-0.5 px-3">
            <div
              v-for="menu in ELEMENT_MENUS"
              :key="menu.path"
              class="flex cursor-pointer items-center gap-2.5 rounded-lg px-3 py-3 text-left text-[13px] transition-all duration-200"
              :class="route.path === menu.path
                ? 'bg-[#a8c4f0] font-medium text-[#0f172a] shadow-sm'
                : 'text-[#475569] hover:bg-white/50 hover:text-[#0f172a]'"
              @click="goMenu(menu.path)"
            >
              <component
                :is="menu.icon"
                :size="16"
                :class="route.path === menu.path ? 'text-[#1e40af]' : 'text-[#64748b]'"
              />
              <span>{{ menu.label }}</span>
            </div>

            <div
              class="mx-2 my-3 border-t border-[#7c8fab]/80"
              role="separator"
              aria-hidden="true"
            />
            <div class="mb-2 px-2 text-[11px] font-bold uppercase tracking-wider text-[#5b6b8c]">
              18项页面设计
            </div>

            <div
              v-for="menu in CORE18_MENUS"
              :key="menu.path"
              class="flex cursor-pointer items-center gap-2.5 rounded-lg px-3 py-3 text-left text-[13px] transition-all duration-200"
              :class="route.path === menu.path
                ? 'bg-[#a8c4f0] font-medium text-[#0f172a] shadow-sm'
                : 'text-[#475569] hover:bg-white/50 hover:text-[#0f172a]'"
              @click="goMenu(menu.path)"
            >
              <component
                :is="menu.icon"
                :size="16"
                :class="route.path === menu.path ? 'text-[#1e40af]' : 'text-[#64748b]'"
              />
              <span>{{ menu.label }}</span>
            </div>

            <div
              class="mx-2 my-3 border-t border-[#7c8fab]/80"
              role="separator"
              aria-hidden="true"
            />
            <div class="mb-2 px-2 text-[11px] font-bold uppercase tracking-wider text-[#5b6b8c]">
              指标中心页面设计
            </div>

            <div
              v-for="menu in INDICATOR_CENTER_MENUS"
              :key="menu.path"
              class="flex cursor-pointer items-center gap-2.5 rounded-lg px-3 py-3 text-left text-[13px] transition-all duration-200"
              :class="route.path === menu.path
                ? 'bg-[#a8c4f0] font-medium text-[#0f172a] shadow-sm'
                : 'text-[#475569] hover:bg-white/50 hover:text-[#0f172a]'"
              @click="goMenu(menu.path)"
            >
              <component
                :is="menu.icon"
                :size="16"
                :class="route.path === menu.path ? 'text-[#1e40af]' : 'text-[#64748b]'"
              />
              <span>{{ menu.label }}</span>
            </div>
          </nav>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="flex min-w-0 flex-1 flex-col overflow-hidden">
        <!-- 面包屑导航 -->
        <div class="h-[48px] shrink-0 bg-[#e8eef9] px-6 py-2.5">
          <div class="flex items-center gap-2 text-[13px] text-[#1F264D]">
            <span>首页</span>
            <span>/</span>
            <span>{{ currentModule }}</span>
          </div>
        </div>

        <!-- 主内容 -->
        <div class="relative flex-1 overflow-y-auto p-6">
          <RouterView v-slot="{ Component }">
            <Transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </Transition>
          </RouterView>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Component } from 'vue'
import {
  Activity,
  BookOpen,
  Building,
  ClipboardList,
  FileSpreadsheet,
  Home,
  Monitor,
  PlayCircle,
  ShieldAlert,
  TrendingUp,
  Users,
} from 'lucide-vue-next'

type MenuItem = { path: string; label: string; icon: Component }

const ELEMENT_MENUS: MenuItem[] = [
  { path: '/dashboard', label: '总览大屏', icon: Activity },
  { path: '/personnel', label: '人员要素监管', icon: Users },
  { path: '/institution', label: '机构要素监管', icon: Building },
  { path: '/technology', label: '技术要素监管', icon: ShieldAlert },
  { path: '/equipment', label: '设备要素监管', icon: Monitor },
]

const CORE18_MENUS: MenuItem[] = [
  { path: '/core18-overview', label: '十八项核心制度总览', icon: BookOpen },
  { path: '/indicator-final', label: '指标分析台', icon: TrendingUp },
]

const INDICATOR_CENTER_MENUS: MenuItem[] = [
  { path: '/indicator-management', label: '指标管理', icon: ClipboardList },
  { path: '/indicator-execution', label: '指标执行', icon: PlayCircle },
  { path: '/report-center', label: '报表中心', icon: FileSpreadsheet },
]

const ALL_MENUS: MenuItem[] = [...ELEMENT_MENUS, ...CORE18_MENUS, ...INDICATOR_CENTER_MENUS]

const route = useRoute()
const router = useRouter()

function goMenu(path: string) {
  router.push(path)
}

const currentModule = computed(() => {
  const path = route.path
  for (const item of ALL_MENUS) {
    if (path === item.path || path.startsWith(`${item.path}/`)) {
      return item.label
    }
  }
  return ''
})
</script>

<style scoped>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>
