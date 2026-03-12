import { Suspense } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { PrivateRoute } from "../core/guards/PrivateRoute"
import { RiskAppLayout } from "../layouts/RiskAppLayout"
import { Login } from "../modules/auth/Login"
import { RiskDashboard } from "../modules/risk/pages/RiskDashboard"
import { ExcelImportPreview } from "../modules/shared/components/ExcelImportPreview"
import { GenericFluidsView } from "../modules/risk/pages/GenericFluidsView"

const Loading = () => <div className="p-4">Loading...</div>

export const AppRoutes = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route element={<PrivateRoute />}>
          <Route element={<RiskAppLayout />}>
            <Route path="/" element={<RiskDashboard />} />
            <Route path="/import-preview" element={<ExcelImportPreview />} />
            <Route path="/generic-fluids" element={<GenericFluidsView />} />
            {/* Add more protected routes here */}
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
