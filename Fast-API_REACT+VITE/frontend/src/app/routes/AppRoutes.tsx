import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from '../modules/auth/Login';
import { Dashboard } from '../modules/dashboard/Dashboard';
import { MainLayout } from '../layouts/MainLayout';
import { PrivateRoute } from '../common/core/guards/PrivateRoute';

export const AppRoutes = () => {
    return (
        <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />

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
    );
};
