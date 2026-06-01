export interface FactTable {
  code: string
  label: string
}

export const FACT_TABLES: FactTable[] = [
  {
    code: 'FACT_ADMN_MDC_HTR_RCD',
    label: '住院诊疗记录',
  },
  {
    code: 'FACT_INHOS_ODR_INFMT',
    label: '住院医嘱信息',
  },
]

export function formatInvolvedTables(codes: string[]): string {
  return codes.filter(Boolean).join(', ')
}

export function parseInvolvedTables(text: string): string[] {
  return text
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}
