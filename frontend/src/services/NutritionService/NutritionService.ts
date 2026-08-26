import { http } from '../../lib/http'
import type { FoodSearchHit, FoodSearchResponse } from '../../types/nutrition'

export const NutritionService = {
  search(q: string, signal?: AbortSignal): Promise<FoodSearchResponse> {
    return http<FoodSearchResponse>(
      `/api/v1/nutrition/search?q=${encodeURIComponent(q.trim())}`,
      { signal },
    )
  },

  get(id: string, signal?: AbortSignal): Promise<FoodSearchHit> {
    return http<FoodSearchHit>(`/api/v1/nutrition/${encodeURIComponent(id)}`, { signal })
  },
}
