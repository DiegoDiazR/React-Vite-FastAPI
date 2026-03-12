import type { AuthResponse, User } from "../models/auth.model"

export const authAdapter = (
  response: AuthResponse,
): { user: User; token: string } => {
  if (!response?.access_token || !response?.user) {
    throw new Error("Invalid authentication response")
  }

  return {
    token: response.access_token,
    user: {
      id: String(response.user.id),
      email: response.user.email,
      fullName: response.user.full_name ?? "",
      roles: Array.isArray(response.user.roles) ? response.user.roles : [],
      permissions: Array.isArray(response.user.permissions)
        ? response.user.permissions
        : [],
    },
  }
}
