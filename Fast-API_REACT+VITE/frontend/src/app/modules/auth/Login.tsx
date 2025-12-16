import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../common/core/store/auth.store';
// import { authService } from '../../common/core/services/auth.service';
// import { normalizeError } from '../../../utils/error-normalizer';
import { useTranslation } from 'react-i18next';

export const Login = () => {
    const { t } = useTranslation();
    const { register, handleSubmit } = useForm();
    const [error, setError] = useState('');
    const login = useAuthStore((state) => state.login);
    const navigate = useNavigate();
    const location = useLocation();

    const from = location.state?.from?.pathname || '/';

    const onSubmit = async (data: any) => {
        try {
            setError('');

            // REAL IMPLEMENTATION (commented for now):
            // const response = await authService.login(data);
            // login(response); // response already contains { user, token }

            // MOCK LOGIN FOR DEMO
            console.log('Logging in with:', data);
            const mockToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

            const mockUser = {
                id: "1",
                email: data.username,
                fullName: "Mock User",
                roles: ["admin"],
                permissions: ["view_dashboard"]
            };

            login({ user: mockUser, token: mockToken });

            navigate(from, { replace: true });
        } catch (err) {
            // REAL IMPLEMENTATION (commented for now):
            // const normalizedError = normalizeError(err);
            // setError(t(normalizedError.message));

            setError(t('auth.login_failed'));
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        {t('common.login')}
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email-address" className="sr-only">
                                {t('auth.email')}
                            </label>
                            <input
                                id="email-address"
                                type="email"
                                autoComplete="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder={t('auth.email')}
                                {...register('username', { required: true })}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                {t('auth.password')}
                            </label>
                            <input
                                id="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder={t('auth.password')}
                                {...register('password', { required: true })}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm text-center">
                            {error}
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            {t('common.login')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
