import { http } from '../../lib/http'
import {
  isAllowedImageFile,
  UNSUPPORTED_IMAGE_MESSAGE,
  type FoodPredictResponse,
} from '../../types/detection'

const PREDICT_ENDPOINT = '/api/v1/food/predict'

export const DetectionService = {
  async analyze(file: File, signal?: AbortSignal): Promise<FoodPredictResponse> {
    if (!isAllowedImageFile(file)) {
      throw new Error(UNSUPPORTED_IMAGE_MESSAGE)
    }
    const body = new FormData()
    body.append('image', file)
    return http<FoodPredictResponse>(PREDICT_ENDPOINT, {
      method: 'POST',
      body,
      signal,
    })
  },
}
