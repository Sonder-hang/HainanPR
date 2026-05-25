<template>
  <div class="flex h-full flex-col">
    <!-- 页面标题栏 -->
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="flex h-8 w-8 items-center justify-center rounded-md bg-blue-50">
          <FileSearch :size="16" class="text-blue-500" />
        </div>
        <div>
          <h1 class="text-[15px] font-semibold text-[#1F264D]">委托第三方检测备案与合规审查</h1>
          <p class="text-[11px] text-[#596080]">第三方检验监管 / 送检机构列表</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="flex items-center gap-1.5 rounded-md border border-[#b8c9e8]/60 bg-white px-3 py-1.5 text-[12px] text-[#596080] transition-colors hover:bg-[#f0f4ff]">
          <Download :size="14" />
          导出列表
        </button>
        <button
          class="flex items-center gap-1.5 rounded-md bg-blue-500 px-3 py-1.5 text-[12px] font-medium text-white shadow-sm transition-colors hover:bg-blue-600"
          @click="$router.push('/third-party-inspection/add')"
        >
          <PlusCircle :size="14" />
          新增备案录入
        </button>
      </div>
    </div>

    <!-- 搜索筛选栏 -->
    <div class="mb-4 flex items-center gap-3 rounded-md border border-[#b8c9e8]/40 bg-white px-4 py-3 shadow-sm">
      <div class="flex items-center gap-2">
        <span class="text-[12px] text-[#596080]">委托医疗机构</span>
        <input
          v-model="searchForm.hospital"
          type="text"
          placeholder="输入机构名称"
          class="w-[160px] rounded border border-[#b8c9e8]/60 px-2 py-1.5 text-[12px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
        />
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[12px] text-[#596080]">受托机构</span>
        <input
          v-model="searchForm.agency"
          type="text"
          placeholder="输入受托机构"
          class="w-[160px] rounded border border-[#b8c9e8]/60 px-2 py-1.5 text-[12px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
        />
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[12px] text-[#596080]">合规状态</span>
        <select
          v-model="searchForm.status"
          class="rounded border border-[#b8c9e8]/60 px-2 py-1.5 text-[12px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
        >
          <option value="">全部</option>
          <option value="合规">合规</option>
          <option value="待审查">待审查</option>
          <option value="材料异常">材料异常</option>
        </select>
      </div>
      <button
        class="rounded-md bg-blue-500 px-3 py-1.5 text-[12px] font-medium text-white transition-colors hover:bg-blue-600"
        @click="handleSearch"
      >
        搜索
      </button>
      <button
        class="rounded-md border border-[#b8c9e8]/60 px-3 py-1.5 text-[12px] text-[#596080] transition-colors hover:bg-[#f0f4ff]"
        @click="resetSearch"
      >
        重置
      </button>
    </div>

    <!-- 列表主体 -->
    <div class="flex-1 overflow-hidden rounded-md border border-[#b8c9e8]/40 bg-white shadow-sm">
      <div class="h-full overflow-y-auto">
        <table class="w-full text-sm text-left">
          <thead class="sticky top-0 z-10 bg-[#f0f4ff] text-[12px] text-[#596080]">
            <tr>
              <th class="px-4 py-3 font-medium">委托医疗机构</th>
              <th class="px-4 py-3 font-medium">受托第三方检测机构</th>
              <th class="px-4 py-3 font-medium">开展检测项目示例</th>
              <th class="px-4 py-3 font-medium">协议有效期至</th>
              <th class="px-4 py-3 font-medium">合规审查状态</th>
              <th class="px-4 py-3 text-right font-medium">监管操作</th>
            </tr>
          </thead>
          <tbody class="text-[13px]">
            <tr
              v-for="item in filteredList"
              :key="item.id"
              class="border-t border-[#b8c9e8]/20 transition-colors hover:bg-[#f8faff]"
            >
              <td class="px-4 py-3 font-medium text-[#1F264D]">{{ item.hospital }}</td>
              <td class="px-4 py-3 text-[#596080]">{{ item.agency }}</td>
              <td class="px-4 py-3 text-[#596080]">
                <span class="max-w-[200px] block truncate" :title="item.project">{{ item.project }}</span>
              </td>
              <td class="px-4 py-3 text-[#596080]">{{ item.date }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-block rounded-full px-2 py-0.5 text-[11px] font-medium"
                  :class="{
                    'bg-green-50 text-green-600': item.status === '合规',
                    'bg-blue-50 text-blue-600': item.status === '待审查',
                    'bg-red-50 text-red-600': item.status === '材料异常',
                  }"
                >{{ item.status }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  class="flex items-center gap-1 text-[12px] font-medium text-blue-500 transition-colors hover:text-blue-700"
                  @click="openModal(item)"
                >
                  <FileSearch :size="13" />
                  查阅档案与协议
                </button>
              </td>
            </tr>
            <tr v-if="filteredList.length === 0">
              <td colspan="6" class="px-4 py-12 text-center text-[13px] text-[#596080]">
                暂无数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 档案弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          v-if="isModalOpen"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm"
          @click.self="closeModal"
        >
          <div class="w-[620px] max-h-[85vh] flex flex-col rounded-lg bg-white shadow-xl overflow-hidden">
            <!-- 弹窗头部 -->
            <div class="flex items-center justify-between border-b border-[#b8c9e8]/40 bg-[#f0f4ff] px-6 py-4">
              <h3 class="flex items-center gap-2 font-semibold text-[#1F264D]">
                <FileText :size="16" class="text-blue-500" />
                材料核实与合规审查 - {{ selectedContract?.hospital }}
              </h3>
              <button
                class="flex h-8 w-8 items-center justify-center rounded-md text-[#596080] transition-colors hover:bg-[#e8eef9] hover:text-[#1F264D]"
                @click="closeModal"
              >
                <X :size="16" />
              </button>
            </div>

            <!-- 弹窗内容 -->
            <div class="flex-1 overflow-y-auto p-6 space-y-5">
              <!-- 基本信息 -->
              <div class="grid grid-cols-2 gap-3 rounded-md border border-[#b8c9e8]/30 bg-[#f8faff] p-4 text-[13px]">
                <div><span class="text-[#596080]">委托医疗机构：</span><span class="font-medium text-[#1F264D]">{{ selectedContract?.hospital }}</span></div>
                <div><span class="text-[#596080]">受托检测机构：</span><span class="font-medium text-[#1F264D]">{{ selectedContract?.agency }}</span></div>
                <div class="col-span-2"><span class="text-[#596080]">开展检测项目：</span><span class="text-[#1F264D]">{{ selectedContract?.project }}</span></div>
              </div>

              <!-- 附件材料 -->
              <div class="rounded-md border border-[#b8c9e8]/40 overflow-hidden">
                <div class="bg-[#f0f4ff] px-4 py-2.5 text-[12px] font-semibold text-[#596080] border-b border-[#b8c9e8]/40">
                  医院上传核验附件材料
                </div>
                <ul>
                  <li
                    v-for="(file, idx) in contractFiles"
                    :key="idx"
                    class="flex items-center justify-between border-b border-[#b8c9e8]/20 px-4 py-3 transition-colors hover:bg-[#f8faff] last:border-0"
                  >
                    <div class="flex items-center gap-2 text-[13px] text-[#1F264D]">
                      <FileText :size="14" :class="file.color" />
                      {{ file.name }}
                    </div>
                    <button class="flex items-center gap-1 rounded bg-blue-50 px-2 py-1 text-[11px] text-blue-500 transition-colors hover:bg-blue-100 hover:text-blue-700">
                      <Download :size="11" />
                      查阅原件
                    </button>
                  </li>
                </ul>
              </div>

              <!-- 协议解析 -->
              <div class="rounded-md border border-blue-200 bg-blue-50 p-4">
                <div class="mb-3 flex items-center justify-between">
                  <div class="text-[13px] font-semibold text-blue-700">协议与纪要关键内容提取</div>
                  <div class="flex items-center gap-1 rounded border border-blue-200 bg-white px-2 py-1 text-[11px] text-blue-500 shadow-sm">
                    <Shield :size="11" />
                    系统智能解析
                  </div>
                </div>
                <ul class="space-y-2 text-[12px] text-blue-700">
                  <li class="flex items-start gap-1.5"><span>•</span><span><strong>合作有效期限：</strong>自协议签订起至 {{ selectedContract?.date }}</span></li>
                  <li class="flex items-start gap-1.5"><span>•</span><span><strong>合规性审核：</strong>已在会议纪要中体现"符合《全国公立医疗机构行风管理核心制度要点》要求"。</span></li>
                  <li class="flex items-start gap-1.5"><span>•</span><span><strong>廉洁条款：</strong>包含反商业贿赂规定（详见协议第8页廉洁协议）。</span></li>
                  <li class="flex items-start gap-1.5"><span>•</span><span><strong>数据安全：</strong>双方已签署《信息保护及数据安全责任》附件。</span></li>
                </ul>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="flex items-center justify-end gap-3 border-t border-[#b8c9e8]/40 bg-[#f8faff] px-6 py-4">
              <button
                class="rounded-md border border-[#b8c9e8]/60 px-4 py-2 text-[13px] text-[#596080] transition-colors hover:bg-[#e8eef9]"
                @click="closeModal"
              >
                关闭
              </button>
              <button
                v-if="selectedContract?.status !== '合规'"
                class="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-[13px] text-red-500 transition-colors hover:bg-red-100"
                @click="closeModal"
              >
                退回补充材料
              </button>
              <button
                class="rounded-md bg-blue-500 px-4 py-2 text-[13px] font-medium text-white shadow-sm transition-colors hover:bg-blue-600"
                @click="closeModal"
              >
                核查无误通过
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  FileSearch, Download, X, PlusCircle, FileText, Shield,
} from 'lucide-vue-next'

interface Contract {
  id: number
  hospital: string
  agency: string
  project: string
  status: string
  date: string
}

const contractList: Contract[] = [
  { id: 1, hospital: '海口市第一人民医院', agency: '海南金域医学检验中心', project: 'X基因检测、肿瘤标志物筛查', status: '合规', date: '2025-12-31' },
  { id: 2, hospital: '海口市人民医院', agency: '广州迪安医学检验实验室', project: '罕见病基因测序', status: '合规', date: '2024-10-15' },
  { id: 3, hospital: '海南省中医院', agency: '北京博奥医学检验所', project: '用药指导基因检测', status: '材料异常', date: '2024-08-20' },
  { id: 4, hospital: '三亚市中心医院', agency: '海南金域医学检验中心', project: '无创产前DNA检测', status: '待审查', date: '2026-05-11' },
  { id: 5, hospital: '琼海市人民医院', agency: '海口金沙医学检验实验室', project: '呼吸道病原体多重核酸检测', status: '合规', date: '2025-06-30' },
  { id: 6, hospital: '儋州市人民医院', agency: '北京博奥医学检验所', project: '个体化用药基因检测', status: '合规', date: '2024-12-31' },
]

const searchForm = ref({ hospital: '', agency: '', status: '' })
const isModalOpen = ref(false)
const selectedContract = ref<Contract | null>(null)

const filteredList = computed(() => {
  return contractList.filter(item => {
    const hMatch = !searchForm.value.hospital || item.hospital.includes(searchForm.value.hospital)
    const aMatch = !searchForm.value.agency || item.agency.includes(searchForm.value.agency)
    const sMatch = !searchForm.value.status || item.status === searchForm.value.status
    return hMatch && aMatch && sMatch
  })
})

const contractFiles = computed(() => [
  { name: `${selectedContract.value?.agency}委托检验协议（外包项目）.pdf`, color: 'text-red-400' },
  { name: '院长办公会/院党委会研究纪要.docx', color: 'text-blue-400' },
  { name: '外送样本检验项目清单及价格表.xlsx', color: 'text-green-400' },
])

function handleSearch() {}
function resetSearch() {
  searchForm.value = { hospital: '', agency: '', status: '' }
}
function openModal(contract: Contract) {
  selectedContract.value = contract
  isModalOpen.value = true
}
function closeModal() {
  isModalOpen.value = false
  selectedContract.value = null
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
