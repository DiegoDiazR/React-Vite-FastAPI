import { Navigate, Route, Routes } from "react-router-dom"
import { PrivateRoute } from "../common/core/guards/PrivateRoute"
import { MainLayout } from "../layouts/MainLayout"
import { ActionPlansPage } from "../modules/actionPlans/pages/ActionPlansPage"
import { Dashboard } from "../modules/dashboard/Dashboard"

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Protected Routes */}
      <Route element={<PrivateRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/action-plans" element={<ActionPlansPage />} />
          {/* Add more protected routes here */}
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
