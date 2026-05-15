import * as XLSX from 'xlsx'

export interface ExcelColumn {
  field: string
  header: string
}

export function exportToExcel<T = Record<string, any>>(
  data: T[],
  columns: ExcelColumn[],
  filename: string
) {
  if (!data || data.length === 0) {
    alert('当前无数据可导出')
    return
  }

  const rows = data.map(item => {
    const row: Record<string, any> = {}
    columns.forEach(col => {
      row[col.header] = (item as any)[col.field]
    })
    return row
  })

  const worksheet = XLSX.utils.json_to_sheet(rows)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '数据导出')

  // 自动列宽
  const colWidths = columns.map(col => ({
    wch: Math.max(
      col.header.length,
      ...rows.map(r => String(r[col.header] ?? '').length)
    )
  }))
  worksheet['!cols'] = colWidths

  XLSX.writeFile(workbook, `${filename}.xlsx`)
}
