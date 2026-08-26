export type FoodServing = {
  unit: string
  grams: number
  milliliters: number | null
  is_default: boolean
}

export type FoodSearchHit = {
  id: string
  slug: string
  name: string
  detect_class_id: number | null
  status: string
  calories_per_100g: number | null
  protein_per_100g: number | null
  carb_per_100g: number | null
  fat_per_100g: number | null
  source_dataset: string | null
  source_id: string | null
  source_note: string | null
  aliases: string[]
  servings: FoodServing[]
}

export type FoodSearchResponse = {
  query: string
  items: FoodSearchHit[]
}

export function defaultServing(hit: FoodSearchHit): FoodServing | null {
  return hit.servings.find((row) => row.is_default) ?? hit.servings[0] ?? null
}

export function estimatedCalories(
  hit: FoodSearchHit,
  unit: string,
  quantity: number,
): number | null {
  if (hit.calories_per_100g == null) {
    return null
  }
  const serving = hit.servings.find((row) => row.unit === unit)
  if (serving == null) {
    return null
  }
  return Math.round((quantity * serving.grams * hit.calories_per_100g) / 100)
}
