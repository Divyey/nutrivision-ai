export type UserPublic = {
  id: string
  name: string
  email: string
}

export type RegisterRequest = {
  name: string
  email: string
  password: string
}

export type LoginRequest = {
  email: string
  password: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type UpdateIdentityRequest = {
  name?: string
  email?: string
}
