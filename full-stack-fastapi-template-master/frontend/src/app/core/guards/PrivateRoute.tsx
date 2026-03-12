import { Outlet, useLocation } from "react-router-dom"
import { useAuthStore } from "../store/auth.store"

export const PrivateRoute = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const _location = useLocation()

  if (!isAuthenticated) {
    const loginUrl = import.meta.env.VITE_LOGIN_URL
    if (loginUrl) {
      window.location.href = loginUrl
      return null
    }
    // If no login URL is configured, we can't do much but maybe show a message or reload
    // to avoid infinite loop if the route doesn't exist.
    // However, since we are in a guard, we should probably just return null or a specific error component.
    // For now, let's return null to prevent rendering the protected content.

    // DEVELOPMENT ONLY: Quick Login Button
    if (import.meta.env.DEV) {
      const handleDevLogin = () => {
        const dummyToken =
          "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRldiBVc2VyIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjQ4OTg0MzMwNzh9.dummy"
        useAuthStore.getState().login({
          user: { id: "dev", username: "Dev User", permissions: [] },
          token: dummyToken,
        })
      }

      return (
        <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-zinc-900">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
              Development Mode
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              You are in dev mode without a parent app.
            </p>
            <button
              type="button"
              onClick={handleDevLogin}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
            >
              Quick Login as Dev User
            </button>
          </div>
        </div>
      )
    }

    return (
      <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-zinc-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            Access Denied
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Please log in to continue.
          </p>
        </div>
      </div>
    )
  }

  return <Outlet />
}
