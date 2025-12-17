import { jwtDecode } from "jwt-decode"
import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"
import type { User } from "../models/auth.model"

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (data: { user: User; token: string }) => void
  logout: () => void
  hasPermission: (permission: string) => boolean
  checkTokenExpiration: () => void
}

interface JwtPayload {
  exp?: number
}

const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode<JwtPayload>(token)
    if (!decoded.exp) return false //validacion de expiracion del token jwt

    const currentTime = Date.now() / 1000
    return decoded.exp < currentTime
  } catch (_error) {
    return true
  }
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: ({ user, token }) => {
        if (isTokenExpired(token)) {
          console.error("Attempted to login with expired token")
          return
        }
        set({ token, user, isAuthenticated: true })
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
      },

      hasPermission: (permission: string) => {
        const { user } = get()
        return user?.permissions?.includes(permission) ?? false
      },

      checkTokenExpiration: () => {
        const { token, logout } = get()
        if (token && isTokenExpired(token)) {
          console.warn("Token expired, logging out.")
          logout()
        }
      },
    }),
    {
      name: "auth-storage",
      version: 1, // Versioning state to prevent hydration errors
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        // Check for token in URL
        const searchParams = new URLSearchParams(window.location.search)
        const tokenFromUrl = searchParams.get("token")

        if (tokenFromUrl) {
          if (!isTokenExpired(tokenFromUrl)) {
            state?.login({
              user: {
                id: "external",
                username: "External User",
                permissions: [],
              },
              token: tokenFromUrl,
            })
            // Clean URL
            window.history.replaceState(
              {},
              document.title,
              window.location.pathname,
            )
          }
        } else if (state?.token && isTokenExpired(state.token)) {
          console.warn("Hydrated token is expired, clearing session.")
          state.logout()
        }
      },
    },
  ),
)
