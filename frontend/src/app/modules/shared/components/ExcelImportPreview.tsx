import { useState, useRef } from "react"
import * as XLSX from "xlsx"
import { Upload, X, Check, FileSpreadsheet, ShieldCheck } from "lucide-react"

export const ExcelImportPreview = () => {
  const [data, setData] = useState<any[]>([])
  const [fileName, setFileName] = useState<string>("")
  const [sheets, setSheets] = useState<{ [key: string]: any[] }>({})
  const [activeSheet, setActiveSheet] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const bstr = evt.target?.result
      const wb = XLSX.read(bstr, { type: "binary" })
      
      const allSheetsData: { [key: string]: any[] } = {}
      wb.SheetNames.forEach(name => {
        const ws = wb.Sheets[name]
        const data = XLSX.utils.sheet_to_json(ws)
        allSheetsData[name] = data
      })

      setSheets(allSheetsData)
      setActiveSheet(wb.SheetNames[0])
      setData(allSheetsData[wb.SheetNames[0]])
    }
    reader.readAsBinaryString(file)
  }

  const handleSheetChange = (sheetName: string) => {
    setActiveSheet(sheetName)
    setData(sheets[sheetName])
  }

  return (
    <div className="flex flex-col h-full bg-[#f8fafc] dark:bg-slate-900 p-6">
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center">
            <FileSpreadsheet className="w-6 h-6 mr-3 text-indigo-600" />
            Data Import Tool
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Preview and validate your records before importing to the database</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 rounded-full border border-indigo-100 dark:border-indigo-800">
            <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400 mr-2" />
            <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-300 uppercase">Power Preview</span>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="flex-1 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden">
        
        {/* Upload Area (If no data) */}
        {!data.length && (
          <div 
            className="flex-1 flex flex-col items-center justify-center p-12 border-4 border-dashed border-slate-100 dark:border-slate-700 m-6 rounded-2xl bg-slate-50/50 dark:bg-slate-800/50 hover:border-indigo-200 dark:hover:border-indigo-700 transition-all cursor-pointer group"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-16 h-16 bg-white dark:bg-slate-700 rounded-2xl shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Upload className="w-8 h-8 text-indigo-600" />
            </div>
            <h3 className="text-lg font-bold text-slate-700 dark:text-slate-200">Upload your data file</h3>
            <p className="text-sm text-slate-400 max-w-xs text-center mt-2 font-medium">Drag and drop your Excel or CSV file here, or click to browse</p>
            <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept=".xlsx, .xls, .csv" className="hidden" />
          </div>
        )}

        {/* Preview Area (If data exists) */}
        {data.length > 0 && (
          <div className="flex-1 flex flex-col min-h-0">
            {/* Sheet Tabs */}
            <div className="flex bg-slate-50 dark:bg-slate-800/80 px-4 pt-4 border-b border-slate-200 dark:border-slate-700">
              {Object.keys(sheets).map(sheetName => (
                <button
                  key={sheetName}
                  onClick={() => handleSheetChange(sheetName)}
                  className={`px-5 py-2 text-xs font-bold rounded-t-lg transition-all border-x border-t ${
                    activeSheet === sheetName 
                      ? "bg-white dark:bg-slate-900 text-indigo-700 dark:text-indigo-400 border-slate-200 dark:border-slate-700 relative top-[1px]" 
                      : "bg-transparent border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  }`}
                >
                  {sheetName}
                </button>
              ))}
            </div>

            {/* Toolbar */}
            <div className="p-4 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-slate-400 mr-2 uppercase">File:</span>
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{fileName}</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-full uppercase tracking-tighter">
                  {data.length} Records
                </span>
                <button 
                  onClick={() => { setData([]); setSheets({}); setActiveSheet(""); setFileName(""); }}
                  className="text-xs font-bold text-red-500 hover:text-red-600 flex items-center px-3 py-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                >
                  <X className="w-3.5 h-3.5 mr-1.5" />
                  Discard
                </button>
              </div>
            </div>

            {/* Table Container */}
            <div className="flex-1 overflow-auto bg-white dark:bg-slate-900">
              <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-800 border-collapse">
                <thead className="bg-slate-50 dark:bg-slate-900 sticky top-0 z-10 border-b border-slate-100 dark:border-slate-800">
                  <tr>
                    <th className="px-3 py-3 text-center text-xs font-bold text-slate-400 w-12 border-r border-slate-100 dark:border-slate-800">#</th>
                    {data.length > 0 && Object.keys(data[0]).map(key => (
                      <th key={key} className="px-4 py-3 text-left text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-widest border-r border-slate-100 dark:border-slate-800 whitespace-nowrap">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-50 dark:divide-slate-800">
                  {data.map((row, i) => (
                    <tr key={i} className="hover:bg-indigo-50/20 dark:hover:bg-indigo-900/10 transition-colors">
                      <td className="px-3 py-2 text-center text-[10px] font-bold text-slate-300 border-r border-slate-50 dark:border-slate-800 italic">{i + 1}</td>
                      {Object.values(row).map((val: any, j) => (
                        <td key={j} className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 border-r border-slate-50 dark:border-slate-800 whitespace-nowrap">
                          {val?.toString() || "-"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Action Footer */}
      {data.length > 0 && (
        <div className="mt-6 flex justify-end space-x-4">
          <button 
            onClick={() => { setData([]); setSheets({}); setActiveSheet(""); setFileName(""); }}
            className="px-6 py-2.5 text-sm font-bold text-slate-500 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button className="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-lg shadow-indigo-200 dark:shadow-none font-bold flex items-center transition-all hover:scale-[1.02]">
            <Check className="w-5 h-5 mr-2" />
            Confirm Import
          </button>
        </div>
      )}
    </div>
  )
}
