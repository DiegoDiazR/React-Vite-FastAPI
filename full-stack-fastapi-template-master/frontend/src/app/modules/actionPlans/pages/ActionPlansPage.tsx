import { useTranslation } from "react-i18next"

export const ActionPlansPage = () => {
  const { t } = useTranslation()

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">
        {t("actionPlans.title")}
      </h1>
      <div className="bg-white dark:bg-zinc-900 shadow rounded-lg p-6">
        <p className="text-gray-600 dark:text-gray-400">
          {t("actionPlans.description")}
        </p>
        {/* Content will go here */}
      </div>
    </div>
  )
}
