import { http } from '../../lib/http'
import type {
  DiaryResponse,
  LogMealsRequest,
  LogWaterRequest,
  MealEntry,
  PatchMealEntryRequest,
  WaterEntry,
} from '../../types/meals'

export const MealService = {
  getDiary(date: string): Promise<DiaryResponse> {
    return http<DiaryResponse>(`/api/v1/meals/diary?date=${encodeURIComponent(date)}`)
  },

  logEntries(payload: LogMealsRequest): Promise<MealEntry[]> {
    return http<MealEntry[]>('/api/v1/meals/entries', {
      method: 'POST',
      body: payload,
    })
  },

  updateEntry(id: string, payload: PatchMealEntryRequest): Promise<MealEntry> {
    return http<MealEntry>(`/api/v1/meals/entries/${id}`, {
      method: 'PATCH',
      body: payload,
    })
  },

  deleteEntry(id: string): Promise<void> {
    return http<void>(`/api/v1/meals/entries/${id}`, { method: 'DELETE' })
  },

  logWater(payload: LogWaterRequest): Promise<WaterEntry> {
    return http<WaterEntry>('/api/v1/meals/water', {
      method: 'POST',
      body: payload,
    })
  },

  deleteWater(id: string): Promise<void> {
    return http<void>(`/api/v1/meals/water/${id}`, { method: 'DELETE' })
  },
}
