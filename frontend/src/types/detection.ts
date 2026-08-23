/** Provisional until ticket 004 defines the prediction response contract. */
export type FoodPredictResponse = unknown

export const ALLOWED_IMAGE_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const

export type AllowedImageMimeType = (typeof ALLOWED_IMAGE_MIME_TYPES)[number]

export const ALLOWED_IMAGE_ACCEPT = ALLOWED_IMAGE_MIME_TYPES.join(',')

export const UNSUPPORTED_IMAGE_MESSAGE = 'Use a JPEG, PNG, or WebP photo.'

const ALLOWED_IMAGE_MIME_SET = new Set<string>([...ALLOWED_IMAGE_MIME_TYPES, 'image/jpg'])

export function isAllowedImageFile(file: File): boolean {
  return ALLOWED_IMAGE_MIME_SET.has(file.type)
}

export type DetectionPhase =
  | { name: 'capture' }
  | { name: 'review'; file: File; previewUrl: string }
  | { name: 'analyzing'; file: File; previewUrl: string }
  | { name: 'completing'; file: File; previewUrl: string; payload: FoodPredictResponse }
  | { name: 'error'; file: File; previewUrl: string; message: string }
  | { name: 'results'; file: File; previewUrl: string; payload: FoodPredictResponse }
