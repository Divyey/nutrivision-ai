/** Ticket 004 prediction contract. Analyzing progress is not model confidence. */

export type FoodBox = {
  x1: number
  y1: number
  x2: number
  y2: number
}

export type FoodPredictItem = {
  class_id: number
  label: string
  confidence: number
  box: FoodBox
}

export type FoodPredictResponse = {
  image_width: number
  image_height: number
  items: FoodPredictItem[]
}

export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const

export type AllowedImageType = (typeof ALLOWED_IMAGE_TYPES)[number]

export const ALLOWED_IMAGE_ACCEPT = ALLOWED_IMAGE_TYPES.join(',')

export const UNSUPPORTED_IMAGE_MESSAGE = 'Use a JPEG, PNG, or WebP photo.'

const ALLOWED_IMAGE_TYPE_SET = new Set<string>([...ALLOWED_IMAGE_TYPES, 'image/jpg'])

export function isAllowedImageFile(file: File): boolean {
  return ALLOWED_IMAGE_TYPE_SET.has(file.type)
}

export type DetectionPhase =
  | { name: 'capture' }
  | { name: 'review'; file: File; previewUrl: string }
  | { name: 'analyzing'; file: File; previewUrl: string }
  | { name: 'completing'; file: File; previewUrl: string; payload: FoodPredictResponse }
  | { name: 'error'; file: File; previewUrl: string; message: string }
  | { name: 'results'; file: File; previewUrl: string; payload: FoodPredictResponse }
