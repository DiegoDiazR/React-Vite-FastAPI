import api from "../../../common/core/interceptors/axios.instance"

export const actionPlansService = {
  getAll: async () => {
    const response = await api.get("/action-plans")
    return response.data
  },

  getById: async (id: string) => {
    const response = await api.get(`/action-plans/${id}`)
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post("/action-plans", data)
    return response.data
  },

  update: async (id: string, data: any) => {
    const response = await api.put(`/action-plans/${id}`, data)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/action-plans/${id}`)
    return response.data
  },
}
