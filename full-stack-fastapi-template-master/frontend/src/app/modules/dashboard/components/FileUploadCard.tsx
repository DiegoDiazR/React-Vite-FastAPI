import { Upload, FileSpreadsheet, Loader2, X } from "lucide-react"
import { useState, useRef } from "react"
import { useTranslation } from "react-i18next"

interface FileUploadCardProps {
    onFileStatusChange?: (status: "idle" | "selected") => void
}

export const FileUploadCard = ({ onFileStatusChange }: FileUploadCardProps) => {
    const { t } = useTranslation()
    const fileInputRef = useRef<HTMLInputElement>(null)

    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "waiting">("idle")

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (file) {
            setSelectedFile(file)
            onFileStatusChange?.("selected")
            // Simulate auto-upload or ready-to-upload
            handleUploadMock(file)
        }
    }

    const handleRemoveFile = () => {
        setSelectedFile(null)
        setUploadStatus("idle")
        onFileStatusChange?.("idle")
        if (fileInputRef.current) {
            fileInputRef.current.value = ""
        }
    }

    const handleUploadMock = (file: File) => {
        setUploadStatus("uploading")
        console.log("Mock uploading file:", file.name)

        // Simulate upload delay
        setTimeout(() => {
            setUploadStatus("waiting")
        }, 1500)
    }

    const triggerFileInput = () => {
        fileInputRef.current?.click()
    }

    return (
        <div className="w-full bg-white dark:bg-zinc-900 shadow-md rounded-lg p-6 flex flex-col items-center justify-center border border-zinc-200 dark:border-zinc-800 transition-colors">

            <div className="w-full flex items-center gap-4">
                {/* Upload Button */}
                {!selectedFile && (
                    <button
                        onClick={triggerFileInput}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
                    >
                        <Upload className="w-4 h-4" />
                        {t("dashboard.upload_button")}
                    </button>
                )}

                {/* Hidden Input */}
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".xlsx, .xls, .csv"
                    className="hidden"
                />

                {/* File Name & Status */}
                <div className="flex items-center gap-2 flex-1 relative h-6 overflow-hidden">

                    {selectedFile ? (
                        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 animate-in fade-in slide-in-from-left-2 w-full">
                            <FileSpreadsheet className="w-5 h-5 text-green-600 shrink-0" />
                            <span className="font-medium truncate max-w-[200px]">{selectedFile.name}</span>

                            {/* Status Message */}
                            {uploadStatus === "uploading" && (
                                <span className="ml-2 text-sm text-indigo-600 flex items-center gap-1">
                                    <Loader2 className="w-3 h-3 animate-spin" /> {t("common.uploading")}
                                </span>
                            )}

                            {uploadStatus === "waiting" && (
                                <span className="ml-2 text-sm text-amber-600 font-medium animate-pulse">
                                    {t("dashboard.waiting_backend")}
                                </span>
                            )}

                            {/* Remove Button - Always visible when file is selected */}
                            <button
                                onClick={handleRemoveFile}
                                className="ml-auto p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-500 hover:text-red-500 transition-colors"
                                title={t("common.remove_file")}
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <span className="text-zinc-400 text-sm italic">{t("dashboard.no_file_selected")}</span>
                    )}

                </div>
            </div>
        </div>
    )
}
