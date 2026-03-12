import axios from "axios"
import { useAuthStore } from "../store/auth.store"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
})

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error

    if (response) {
      switch (response.status) {
        case 401: {
          // Auto logout on 401
          useAuthStore.getState().logout()

          // Redirect to external login
          const loginUrl = import.meta.env.VITE_LOGIN_URL
          if (loginUrl) {
            window.location.href = loginUrl
          } else {
            // If no external URL, reload to let parent handle it or show unauthorized
            window.location.reload()
          }
          break
        }
        case 403:
          console.error("Permission denied")
          break
        case 500:
          console.error("Server error")
          break
        default:
          break
      }
    }

    return Promise.reject(error)
  },
)

export default api
