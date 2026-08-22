import { http } from '../../lib/http'
import { setAccessToken } from '../../lib/token'
import type { LoginRequest, RegisterRequest, TokenResponse, UserPublic } from '../../types/auth'

export const AuthService = {
  register(payload: RegisterRequest): Promise<UserPublic> {
    return http<UserPublic>('/api/v1/auth/register', {
      method: 'POST',
      body: payload,
      auth: false,
    })
  },

  async login(payload: LoginRequest): Promise<TokenResponse> {
    const token = await http<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: payload,
      auth: false,
    })
    setAccessToken(token.access_token)
    return token
  },

  me(): Promise<UserPublic> {
    return http<UserPublic>('/api/v1/auth/me')
  },
}
