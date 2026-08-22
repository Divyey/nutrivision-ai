import { http } from '../../lib/http'
import type { UpdateProfileRequest, UserProfile } from '../../types/user'

export const UserService = {
  getMe(): Promise<UserProfile> {
    return http<UserProfile>('/api/v1/users/me')
  },

  updateMe(payload: UpdateProfileRequest): Promise<UserProfile> {
    return http<UserProfile>('/api/v1/users/me', {
      method: 'PATCH',
      body: payload,
    })
  },
}
