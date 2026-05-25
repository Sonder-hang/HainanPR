<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题栏 -->
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="flex h-8 w-8 items-center justify-center rounded-md bg-blue-50">
          <FileText :size="16" class="text-blue-500" />
        </div>
        <div>
          <h1 class="text-[15px] font-semibold text-[#1F264D]">医疗机构委托第三方检验协议备案申请</h1>
          <p class="text-[11px] text-[#596080]">第三方检验监管 / 新增备案录入</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="rounded bg-blue-50 px-2 py-1 text-[11px] text-blue-600">表号: HNKM-MP01.01.03</span>
        <button
          class="flex items-center gap-1.5 rounded-md border border-[#b8c9e8]/60 bg-white px-3 py-1.5 text-[12px] text-[#596080] transition-colors hover:bg-[#f0f4ff]"
          @click="$router.push('/third-party-inspection')"
        >
          返回列表
        </button>
      </div>
    </div>

    <!-- 表单卡片 -->
    <div class="rounded-md border border-[#b8c9e8]/40 bg-white shadow-sm overflow-hidden">
      <!-- 标题区 -->
      <div class="flex items-center justify-between border-b border-[#b8c9e8]/40 bg-[#f0f4ff] px-6 py-4">
        <h2 class="flex items-center gap-2 text-[14px] font-semibold text-[#1F264D]">
          <FileText :size="16" class="text-blue-500" />
          医疗机构委托第三方检验协议备案申请
        </h2>
      </div>

      <form class="p-6 space-y-8" @submit.prevent="handleSubmit">
        <!-- 第一部分：协议基础信息 -->
        <section>
          <h3 class="mb-4 flex items-center gap-2 border-l-4 border-blue-500 pl-2 text-[13px] font-bold text-[#1F264D]">
            第一部分：协议基础信息
          </h3>
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label class="mb-1 block text-[12px] font-medium text-[#596080]">
                委托方 (甲方-本机构) <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.hospital"
                type="text"
                class="w-full cursor-not-allowed rounded-md border border-[#b8c9e8]/60 bg-[#f8faff] px-3 py-2 text-[13px] text-[#1F264D]"
                placeholder="请输入本机构名称"
                required
              />
            </div>
            <div>
              <label class="mb-1 block text-[12px] font-medium text-[#596080]">
                受托方 (乙方-第三方检验机构) <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.agency"
                class="w-full rounded-md border border-[#b8c9e8]/60 px-3 py-2 text-[13px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
                required
              >
                <option value="">-- 请选择合作机构 --</option>
                <option value="海南金域医学检验中心有限公司">海南金域医学检验中心有限公司</option>
                <option value="广州迪安医学检验实验室">广州迪安医学检验实验室</option>
                <option value="北京博奥医学检验所">北京博奥医学检验所</option>
                <option value="海口金沙医学检验实验室">海口金沙医学检验实验室</option>
                <option value="other">其他机构 (需补充资质)</option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-[12px] font-medium text-[#596080]">
                委托起始日期 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.startDate"
                type="date"
                class="w-full rounded-md border border-[#b8c9e8]/60 px-3 py-2 text-[13px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
                required
              />
            </div>
            <div>
              <label class="mb-1 block text-[12px] font-medium text-[#596080]">
                委托截止日期 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.endDate"
                type="date"
                class="w-full rounded-md border border-[#b8c9e8]/60 px-3 py-2 text-[13px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
                required
              />
            </div>
          </div>
        </section>

        <!-- 第二部分：检验项目 -->
        <section>
          <h3 class="mb-4 flex items-center gap-2 border-l-4 border-blue-500 pl-2 text-[13px] font-bold text-[#1F264D]">
            第二部分：委托检验项目概述
          </h3>
          <div>
            <label class="mb-1 block text-[12px] font-medium text-[#596080]">
              主要委托项目分类/名称 (如：X基因检测、肿瘤标志物等)
            </label>
            <textarea
              v-model="form.projectDesc"
              rows="3"
              class="w-full rounded-md border border-[#b8c9e8]/60 px-3 py-2 text-[13px] text-[#1F264D] focus:border-blue-400 focus:outline-none"
              placeholder="请简要描述委托检验的项目范围，详细清单请在下方以附件形式上传..."
            />
          </div>
        </section>

        <!-- 第三部分：合规材料上传 -->
        <section>
          <div class="mb-4 flex items-center gap-2">
            <h3 class="flex items-center gap-2 border-l-4 border-blue-500 pl-2 text-[13px] font-bold text-[#1F264D]">
              第三部分：合规备查材料上传
            </h3>
            <div class="flex items-center gap-1 rounded border border-amber-200 bg-amber-50 px-2 py-1 text-[10px] text-amber-600">
              <Info :size="11" />
              请确保上传材料包含《信息保护及数据安全责任》及《廉洁协议》条款
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div
              v-for="upload in uploadItems"
              :key="upload.id"
              class="upload-box flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-[#b8c9e8]/60 bg-[#f8faff] p-4 text-center cursor-pointer transition-colors hover:border-blue-400 hover:bg-blue-50"
              @click="triggerUpload(upload.id)"
            >
              <UploadCloud :size="22" class="mb-2 text-blue-400" />
              <span class="text-[13px] font-medium text-[#1F264D]">{{ upload.label }}</span>
              <span class="mt-1 text-[10px] text-[#596080]">{{ upload.hint }}</span>
              <div v-if="uploadedFiles[upload.id]" class="mt-2 flex items-center gap-1 text-[11px] text-green-500">
                <CheckCircle :size="12" />
                已上传
              </div>
              <input
                :ref="el => { uploadRefs[upload.id] = el as HTMLInputElement }"
                type="file"
                class="hidden"
                :accept="upload.accept"
                @change="handleFileChange($event, upload.id)"
              />
            </div>
          </div>
        </section>

        <!-- 底部操作栏 -->
        <div class="flex items-center justify-end gap-3 border-t border-[#b8c9e8]/40 pt-4">
          <button
            type="button"
            class="rounded-md border border-[#b8c9e8]/60 px-5 py-2 text-[13px] font-medium text-[#596080] transition-colors hover:bg-[#f0f4ff]"
            @click="$router.push('/third-party-inspection')"
          >
            取消
          </button>
          <button
            type="submit"
            class="flex items-center gap-1.5 rounded-md bg-blue-500 px-5 py-2 text-[13px] font-medium text-white shadow-sm transition-colors hover:bg-blue-600"
          >
            <CheckCircle :size="14" />
            提交备案审查
          </button>
        </div>
      </form>
    </div>

    <!-- 提交成功遮罩 -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="submitSuccess"
          class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm"
        >
          <CheckCircle :size="56" class="mb-4 animate-bounce text-green-500" />
          <h3 class="text-xl font-bold text-[#1F264D]">备案申请已提交</h3>
          <p class="mt-2 text-sm text-[#596080]">已流转至监管端大屏等待审核...</p>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  FileText, UploadCloud, CheckCircle, Info,
} from 'lucide-vue-next'

const router = useRouter()

const form = reactive({
  hospital: '海口市第一人民医院',
  agency: '',
  startDate: '',
  endDate: '',
  projectDesc: '',
})

const uploadItems = [
  { id: 'protocol', label: '委托检验协议原件', hint: '支持 PDF/JPG，需含签章', accept: '.pdf,.jpg,.jpeg,.png' },
  { id: 'minutes', label: '党委会/办公会纪要', hint: '支持 DOCX/PDF', accept: '.docx,.pdf' },
  { id: 'price', label: '检验项目清单及价格表', hint: '支持 XLSX/PDF', accept: '.xlsx,.pdf' },
]

const uploadedFiles = ref<Record<string, boolean>>({})
const uploadRefs = ref<Record<string, HTMLInputElement | null>>({})
const submitSuccess = ref(false)

function triggerUpload(id: string) {
  uploadRefs.value[id]?.click()
}

function handleFileChange(event: Event, id: string) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    uploadedFiles.value[id] = true
  }
}

function handleSubmit() {
  submitSuccess.value = true
  setTimeout(() => {
    router.push('/third-party-inspection')
  }, 2000)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
