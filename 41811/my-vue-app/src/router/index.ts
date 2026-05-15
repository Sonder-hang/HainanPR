import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/dashboard/MainDashboardView.vue'),
  },
  {
    path: '/personnel',
    name: 'personnel',
    component: () => import('../views/modules/PersonnelModuleView.vue'),
  },
  {
    path: '/institution',
    name: 'institution',
    component: () => import('../views/modules/InstitutionModuleView.vue'),
  },
  {
    path: '/technology',
    name: 'technology',
    component: () => import('../views/modules/TechnologyModuleView.vue'),
  },
  {
    path: '/equipment',
    name: 'equipment',
    component: () => import('../views/modules/EquipmentModuleView.vue'),
  },
  {
    path: '/core18-overview',
    name: 'core18-overview',
    component: () => import('../views/core18Overview/index.vue'),
  },
  {
    path: '/indicator-final',
    name: 'indicator-final',
    component: () => import('../views/core18IndicatorFinal/index.vue'),
  },
  {
    path: '/indicator-management',
    name: 'indicator-management',
    component: () => import('../views/indicatorManagement/IndicatorManagementView.vue'),
  },
  {
    path: '/indicator-management/new',
    name: 'indicator-management-new',
    component: () => import('../views/indicatorManagement/IndicatorText2SqlAddView.vue'),
  },
  {
    path: '/indicator-management/sql-add',
    name: 'indicator-management-sql-add',
    component: () => import('../views/indicatorManagement/IndicatorSqlAddView.vue'),
  },
  {
    path: '/indicator-execution',
    name: 'indicator-execution',
    component: () => import('../views/indicatorExecution/IndicatorExecutionView.vue'),
  },
  {
    path: '/report-center',
    name: 'report-center',
    component: () => import('../views/reportCenter/ReportCenterView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
