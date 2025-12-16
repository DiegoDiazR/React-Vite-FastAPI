import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../common/core/store/auth.store';
import { useTranslation } from 'react-i18next';

export const MainLayout = () => {
    const { t } = useTranslation();
    const logout = useAuthStore((state) => state.logout);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md">
                <div className="p-4 border-b">
                    <h1 className="text-xl font-bold text-gray-800">MyApp</h1>
                </div>
                <nav className="p-4">
                    <ul className="space-y-2">
                        <li>
                            <Link to="/" className="block p-2 text-gray-700 hover:bg-gray-50 rounded">
                                {t('common.dashboard')}
                            </Link>
                        </li>
                        {/* Add more links here based on permissions */}
                    </ul>
                </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="bg-white shadow-sm z-10">
                    <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                        <h2 className="text-lg font-semibold text-gray-800">
                            {t('common.welcome')}
                        </h2>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 text-sm text-red-600 hover:text-red-800"
                        >
                            {t('common.logout')}
                        </button>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Outlet />
                </main>

                {/* Footer */}
                <footer className="bg-white border-t p-4 text-center text-sm text-gray-600">
                    &copy; {new Date().getFullYear()} MyApp. All rights reserved.
                </footer>
            </div>
        </div>
    );
};
