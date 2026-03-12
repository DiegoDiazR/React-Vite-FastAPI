import { useTranslation } from "react-i18next"

export const Dashboard = () => {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      {/* Welcome Card */}
      <div className="bg-white dark:bg-zinc-900 shadow rounded-lg p-6 transition-colors">
        <h1 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">
          {t("common.dashboard")}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t("dashboard.welcome_message")}
        </p>
      </div>

      {/* Example Inputs Card */}
      <div className="bg-white dark:bg-zinc-900 shadow rounded-lg p-6 transition-colors">
        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-zinc-100">
          {t("dashboard.example_form")}
        </h2>
        <div className="space-y-4 max-w-md">
          {/* Text Input */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1"
            >
              {t("dashboard.email_label")}
            </label>
            <input
              type="email"
              id="email"
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-500 dark:focus:ring-zinc-400 transition-colors"
              placeholder="you@example.com"
            />
          </div>

          {/* Select Input */}
          <div>
            <label
              htmlFor="role"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1"
            >
              {t("dashboard.role_label")}
            </label>
            <select
              id="role"
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-500 dark:focus:ring-zinc-400 transition-colors"
            >
              <option value="user">{t("dashboard.roles.user")}</option>
              <option value="admin">{t("dashboard.roles.admin")}</option>
              <option value="editor">{t("dashboard.roles.editor")}</option>
            </select>
          </div>

          {/* Checkbox */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="notifications"
              className="w-4 h-4 text-zinc-600 border-zinc-300 rounded focus:ring-zinc-500 dark:bg-zinc-800 dark:border-zinc-700"
            />
            <label
              htmlFor="notifications"
              className="text-sm text-zinc-700 dark:text-zinc-300"
            >
              {t("dashboard.notifications_label")}
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
