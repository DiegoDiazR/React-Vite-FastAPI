import clsx from "clsx"
import { useTranslation } from "react-i18next"
import { Link, useLocation } from "react-router-dom"
import { useAuthStore } from "../../core/store/auth.store"

export const Sidebar = () => {
  const { t } = useTranslation()
  const location = useLocation()
  const { isAuthenticated } = useAuthStore()

  const menuItems = [
    { path: "/", label: "common.dashboard", icon: "Home" },
  ]

  if (!isAuthenticated) return null

  return (
    <aside className="w-64 bg-white dark:bg-zinc-900 text-zinc-600 dark:text-zinc-300 border-r border-zinc-200 dark:border-zinc-800 flex flex-col h-full transition-colors">
      <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
        <h1 className="text-xl font-bold text-zinc-900 dark:text-white tracking-tight">
          Protocol
        </h1>
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        <div className="px-4 mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-500">
          {t("common.menu")}
        </div>
        <ul className="space-y-1 px-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={clsx(
                  "flex items-center px-4 py-2 text-sm rounded-md transition-colors",
                  location.pathname === item.path
                    ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white"
                    : "hover:bg-zinc-100/50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-white",
                )}
              >
                {t(item.label)}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800">
        <div className="text-xs text-zinc-500">v1.0.0</div>
      </div>
    </aside>
  )
}
