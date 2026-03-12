import { Navigate, Outlet } from "react-router-dom"
import { useAuthStore } from "../store/auth.store"

interface PermissionRouteProps {
  requiredPermission: string
}

export const PermissionRoute = ({
  requiredPermission,
}: PermissionRouteProps) => {
  const hasPermission = useAuthStore((state) => state.hasPermission)

  if (!hasPermission(requiredPermission)) {
    return <Navigate to="/" replace /> // Redirect to home or unauthorized page
  }

  return <Outlet />
}
