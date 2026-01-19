import { BarChart, PieChart, Activity } from "lucide-react"
import { useTranslation } from "react-i18next"

export const AnalysisCharts = () => {
    const { t } = useTranslation()

    return (
        <div className="w-full space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Header */}
            <div className="flex items-center gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-4">
                <Activity className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                    {t("dashboard.analysis_results")}
                </h2>
            </div>

            {/* Grid of Mock Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Mock Chart 1 */}
                <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-medium text-zinc-700 dark:text-zinc-300">{t("dashboard.chart_distribution")}</h3>
                        <PieChart className="w-5 h-5 text-gray-400" />
                    </div>
                    <div className="h-48 bg-zinc-100 dark:bg-zinc-800 rounded flex items-center justify-center text-zinc-400 text-sm">
                        [ {t("dashboard.chart_placeholder")} ]
                    </div>
                </div>

                {/* Mock Chart 2 */}
                <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-medium text-zinc-700 dark:text-zinc-300">{t("dashboard.chart_performance")}</h3>
                        <BarChart className="w-5 h-5 text-gray-400" />
                    </div>
                    <div className="h-48 bg-zinc-100 dark:bg-zinc-800 rounded flex items-center justify-center text-zinc-400 text-sm">
                        [ {t("dashboard.chart_placeholder")} ]
                    </div>
                </div>

            </div>
        </div>
    )
}
