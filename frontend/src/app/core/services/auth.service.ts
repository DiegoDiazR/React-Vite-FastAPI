import { authAdapter } from "../adapters/auth.adapter"
import api from "../interceptors/axios.instance"
import type { AuthResponse } from "../models/auth.model"

export const authService = {
  login: async (credentials: any) => {
    const response = await api.post<AuthResponse>("/auth/login", credentials)
    // Here we decouple the API response from the UI
    return authAdapter(response.data)
  },

  // Example of another protected endpoint
  getProfile: async () => {
    const response = await api.get("/users/me")
    return response.data
  },
}
