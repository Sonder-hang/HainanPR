/**
 * 统一的 HTTP 客户端
 */
import { API_BASE_URL } from './api'

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>
}

class HttpClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private buildUrl(url: string, params?: Record<string, string | number | boolean | undefined>): string {
    if (!params) return url

    const urlObj = new URL(url.replace(/\/$/, ''), this.baseUrl)
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        urlObj.searchParams.append(key, String(value))
      }
    })
    return urlObj.toString()
  }

  private async request<T>(
    method: string,
    url: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { params, body, ...fetchOptions } = options
    const finalUrl = this.buildUrl(url, params)

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    }

    const config: RequestInit = {
      method,
      headers,
      redirect: 'follow',
      ...fetchOptions,
    }

    if (body && method !== 'GET') {
      config.body = JSON.stringify(body)
    }

    const response = await fetch(finalUrl, config)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`)
    }

    const text = await response.text()
    if (!text.trim()) return {} as T
    try {
      return JSON.parse(text) as T
    } catch {
      return {} as T
    }
  }

  get<T>(url: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('GET', url, options)
  }

  post<T>(url: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('POST', url, { ...options, body })
  }

  put<T>(url: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('PUT', url, { ...options, body })
  }

  delete<T>(url: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('DELETE', url, options)
  }

  /**
   * 流式请求（SSE）
   */
  async *stream(url: string, body?: unknown): AsyncGenerator<string, void, unknown> {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (trimmed.startsWith('data: ')) {
            yield trimmed.slice(6)
          } else if (trimmed) {
            yield trimmed
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }
}

export const httpClient = new HttpClient()
