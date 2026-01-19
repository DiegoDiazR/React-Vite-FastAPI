import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Play } from "lucide-react"
import { FileUploadCard } from "../components/FileUploadCard"
import { AnalysisCharts } from "../components/AnalysisCharts"

export const Dashboard = () => {
  const { t } = useTranslation()
  const [hasFile, setHasFile] = useState(false)
  const [showCharts, setShowCharts] = useState(false)

  const handleFileStatusChange = (status: "idle" | "selected") => {
    setHasFile(status === "selected")
    if (status === "idle") {
      setShowCharts(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] space-y-8">

      {/* 1. File Upload Section */}
      <FileUploadCard onFileStatusChange={handleFileStatusChange} />

      {/* 2. Action Section: Start This Analysis */}
      {hasFile && !showCharts && (
        <div className="flex justify-center animate-in fade-in slide-in-from-top-4">
          <button
            onClick={() => setShowCharts(true)}
            className="group flex items-center gap-3 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-8 py-3 rounded-full font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <Play className="w-5 h-5 fill-current" />
            {t("dashboard.start_analysis")}
          </button>
        </div>
      )}

      {/* 3. Results Section */}
      {showCharts && (
        <AnalysisCharts />
      )}

    </div>
  )
}
