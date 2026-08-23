export const MEAL_SLOTS = ['breakfast', 'lunch', 'snacks', 'dinner'] as const

export type MealSlot = (typeof MEAL_SLOTS)[number]

export const MEAL_SLOT_LABELS: Record<MealSlot, string> = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  snacks: 'Snacks',
  dinner: 'Dinner',
}

/** Number of default servings. 1 = dish_nutrition.default_serving_grams grams. */
export type MealItemInput = {
  class_id: number
  quantity: number
}

export type LogMealsRequest = {
  logged_on: string
  slot: MealSlot
  items: MealItemInput[]
}

export type PatchMealEntryRequest = {
  quantity?: number
  slot?: MealSlot
}

export type LogWaterRequest = {
  logged_on: string
  milliliters: number
}

export type MealEntry = {
  id: string
  logged_on: string
  slot: MealSlot
  source: string
  class_id: number
  label: string
  quantity: number
  calories: number
  protein: number
  carb: number
  fat: number
}

export type WaterEntry = {
  id: string
  logged_on: string
  milliliters: number
}

export type MacroTotals = {
  calories: number
  protein: number
  carb: number
  fat: number
}

export type DiaryResponse = {
  date: string
  slots: Record<MealSlot, MealEntry[]>
  water: {
    milliliters: number
    entries: WaterEntry[]
  }
  totals: MacroTotals
}

const LOCAL_DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/

export function localDateString(value: Date = new Date()): string {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/** Calendar Date for a YYYY-MM-DD string in local time, or null if invalid. */
export function dateFromLocalDateString(value: string): Date | null {
  const match = LOCAL_DATE_RE.exec(value)
  if (match == null) {
    return null
  }
  const year = Number(match[1])
  const month = Number(match[2])
  const day = Number(match[3])
  const date = new Date(year, month - 1, day)
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
    return null
  }
  return date
}

export function parseLocalDateString(value: string | null): string | null {
  if (value == null || dateFromLocalDateString(value) == null) {
    return null
  }
  return value
}

/** Diary date: valid YYYY-MM-DD, never after today. Invalid or future → today. */
export function resolveDiaryDate(value: string | null, today: string = localDateString()): string {
  const parsed = parseLocalDateString(value)
  if (parsed == null || parsed > today) {
    return today
  }
  return parsed
}

export function shiftLocalDateString(value: string, days: number): string {
  const date = dateFromLocalDateString(value)
  if (date == null) {
    return value
  }
  date.setDate(date.getDate() + days)
  return localDateString(date)
}

/** Sunday, 23 Aug 2026 */
export function formatWeekdayDate(value: Date | string = new Date()): string {
  const date = typeof value === 'string' ? dateFromLocalDateString(value) : value
  const resolved = date ?? new Date()
  const weekday = resolved.toLocaleDateString('en-GB', { weekday: 'long' })
  const rest = resolved.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
  return `${weekday}, ${rest}`
}

export function displayFoodLabel(slug: string): string {
  return slug
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function isMealSlot(value: string | null): value is MealSlot {
  return value != null && (MEAL_SLOTS as readonly string[]).includes(value)
}
