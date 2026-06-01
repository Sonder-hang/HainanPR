import { ref, computed } from 'vue'

export interface Hospital {
  id: string
  name: string
  level: string
}

export const hospitals: Hospital[] = [
  { id: 'all', name: '全省', level: '' },
  { id: 'h001', name: '省立第一医院', level: '三级甲等' },
  { id: 'h002', name: '市中心医院', level: '三级甲等' },
  { id: 'h003', name: '省肿瘤医院', level: '三级甲等' },
  { id: 'h004', name: '县人民医院', level: '二级甲等' },
  { id: 'h005', name: '省立第三医院', level: '三级乙等' },
  { id: 'h006', name: '县第二医院', level: '二级乙等' },
  { id: 'h007', name: '康华医院', level: '二级甲等（民营）' },
  { id: 'h008', name: '仁爱医院', level: '一级甲等（民营）' },
]

export const currentHospitalId = ref('all')

export const currentHospital = computed(() =>
  hospitals.find(h => h.id === currentHospitalId.value) || hospitals[0]
)
