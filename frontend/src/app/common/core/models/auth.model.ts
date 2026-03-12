// Domain Entity (Frontend View)
export interface User {
  id: string
  email: string
  fullName: string
  roles: string[]
  permissions: string[]
}

// API Response Contract (Backend View)
export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    full_name: string
    roles: string[]
    permissions: string[]
  }
}
