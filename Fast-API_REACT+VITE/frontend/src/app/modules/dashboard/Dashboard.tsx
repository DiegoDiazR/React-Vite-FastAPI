import { useTranslation } from 'react-i18next';

export const Dashboard = () => {
    const { t } = useTranslation();

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold mb-4">{t('common.dashboard')}</h1>
            <p className="text-gray-600">
                Welcome to your dashboard. This is a protected route.
            </p>
        </div>
    );
};
