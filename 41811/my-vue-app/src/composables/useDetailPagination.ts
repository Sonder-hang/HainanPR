import { computed, ref, watch, type MaybeRefOrGetter } from 'vue'
import { toValue } from 'vue'

export interface DetailPaginationOptions<T> {
  rows: MaybeRefOrGetter<T[]>
  pageSize?: MaybeRefOrGetter<number>
  resetDeps?: MaybeRefOrGetter<unknown>[]
}

export function useDetailPagination<T>(options: DetailPaginationOptions<T>) {
  const currentPage = ref(1)

  const resolvedPageSize = computed(() => {
    const size = Number(toValue(options.pageSize ?? 10))
    return Number.isFinite(size) && size > 0 ? size : 10
  })

  const sourceRows = computed<T[]>(() => {
    const rows = toValue(options.rows)
    return Array.isArray(rows) ? rows : []
  })

  const totalCount = computed(() => sourceRows.value.length)
  const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / resolvedPageSize.value)))

  const visiblePages = computed(() => {
    const maxVisible = 5
    let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
    let end = Math.min(totalPages.value, start + maxVisible - 1)

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1)
    }

    const pages: number[] = []
    for (let page = start; page <= end; page++) {
      pages.push(page)
    }
    return pages
  })

  const pagedRows = computed(() => {
    const start = (currentPage.value - 1) * resolvedPageSize.value
    return sourceRows.value.slice(start, start + resolvedPageSize.value)
  })

  function prevPage() {
    if (currentPage.value > 1) currentPage.value--
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) currentPage.value++
  }

  function goToPage(page: number) {
    currentPage.value = Math.min(Math.max(1, page), totalPages.value)
  }

  function resetPage() {
    currentPage.value = 1
  }

  watch([sourceRows, totalPages], () => {
    if (currentPage.value > totalPages.value) {
      currentPage.value = totalPages.value
    }
    if (currentPage.value < 1) {
      currentPage.value = 1
    }
  }, { immediate: true })

  if (options.resetDeps?.length) {
    watch(options.resetDeps.map(dep => () => toValue(dep)), () => {
      resetPage()
    })
  }

  return {
    currentPage,
    totalCount,
    totalPages,
    visiblePages,
    pagedRows,
    prevPage,
    nextPage,
    goToPage,
    resetPage,
  }
}
