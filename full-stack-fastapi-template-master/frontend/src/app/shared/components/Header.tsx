import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import clsx from "clsx"
import { Check, ChevronDown, Globe, LogOut, Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { useTranslation } from "react-i18next"
import { toast } from "sonner"
import { useAuthStore } from "../../core/store/auth.store"

export const Header = () => {
  const { t, i18n } = useTranslation()
  const { theme, setTheme } = useTheme()
  const logout = useAuthStore((state) => state.logout)

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const handleLogout = () => {
    const loginUrl = import.meta.env.VITE_LOGIN_URL
    if (!loginUrl) {
      toast.warning(t("common.logout_disabled_dev"), {
        description: "VITE_LOGIN_URL is not configured.",
      })
      return
    }
    logout()
  }

  const languages = [
    { code: "en", label: "EN" },
    { code: "es", label: "ES" },
    { code: "pt", label: "PT" },
  ]

  return (
    <header className="h-16 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between px-6 transition-colors">
      {/* Left: Breadcrumbs or Title */}
      <div className="flex items-center">
        <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
          {t("common.dashboard")}
        </h2>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4">
        {/* Language Dropdown */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button
              type="button"
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md transition-colors outline-none"
            >
              <Globe className="w-4 h-4" />
              <span>{i18n.language.toUpperCase()}</span>
              <ChevronDown className="w-3 h-3 opacity-50" />
            </button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="min-w-[120px] bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md shadow-lg p-1 z-50 animate-in fade-in zoom-in-95 duration-100"
              sideOffset={5}
            >
              {languages.map((lang) => (
                <DropdownMenu.Item
                  key={lang.code}
                  className={clsx(
                    "flex items-center justify-between px-3 py-2 text-sm rounded-sm cursor-pointer outline-none",
                    i18n.language === lang.code
                      ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
                      : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-zinc-200",
                  )}
                  onClick={() => i18n.changeLanguage(lang.code)}
                >
                  <span>{lang.label}</span>
                  {i18n.language === lang.code && (
                    <Check className="w-3 h-3 text-zinc-900 dark:text-zinc-100" />
                  )}
                </DropdownMenu.Item>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        {/* Theme Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="p-2 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors relative w-10 h-10 flex items-center justify-center"
          aria-label="Toggle Theme"
        >
          <Sun className="h-5 w-5 absolute transition-all duration-300 rotate-0 scale-100 dark:-rotate-90 dark:scale-0" />
          <Moon className="h-5 w-5 absolute transition-all duration-300 rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
        </button>

        {/* Logout */}
        <button
          type="button"
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>{t("common.logout")}</span>
        </button>
      </div>
    </header>
  )
}
