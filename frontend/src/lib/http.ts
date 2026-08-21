import { getAccessToken } from './token'

function apiBase(): string {
  const base = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/$/, '')
  if (!base) {
    throw new Error('Set VITE_API_BASE_URL (local: http://127.0.0.1:8000)')
  }
  return base
}

export class HttpError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'HttpError'
    this.status = status
  }
}

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail) && detail[0] && typeof detail[0] === 'object' && 'msg' in detail[0]) {
      return String((detail[0] as { msg: string }).msg)
    }
  }
  if (status === 401) {
    return 'Not authenticated'
  }
  return 'Request failed'
}

export async function http<T>(
  path: string,
  options: {
    method?: string
    body?: unknown
    auth?: boolean
  } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
  }
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (options.auth !== false) {
    const token = getAccessToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${apiBase()}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  })

  const payload: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    throw new HttpError(response.status, errorMessage(response.status, payload))
  }
  return payload as T
}
