import React, { Suspense } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { PrivateRoute } from "../core/guards/PrivateRoute"
import { MainLayout } from "../layouts/MainLayout"

const Dashboard = React.lazy(() => import("../modules/dashboard/pages/Dashboard").then(module => ({ default: module.Dashboard })))

const Loading = () => <div className="p-4">Loading...</div>

export const AppRoutes = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Protected Routes */}
        <Route element={<PrivateRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            {/* Add more protected routes here */}
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
