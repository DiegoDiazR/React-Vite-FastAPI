import { Wrench, Edit, Search, ChevronRight } from "lucide-react"

export const RiskDashboard = () => {

  return (
    <div className="flex flex-col h-full items-center justify-center bg-[#f8fafc] dark:bg-slate-950">
      
      {/* Centered Logo/Title Area */}
      <div className="flex items-center space-x-3 mb-16">
        <h1 className="text-5xl font-light text-slate-900 dark:text-slate-100 tracking-tight">
          CoreRisk <sup className="text-xs text-indigo-600 font-bold">®</sup>
        </h1>
        <div className="w-14 h-14 rounded-2xl bg-indigo-700 dark:bg-indigo-600 flex items-center justify-center text-white text-3xl font-bold shadow-xl rotate-3">
          C
        </div>
      </div>

      {/* Main Action Buttons */}
      <div className="flex flex-col space-y-4 w-full max-w-lg">
        
        <button className="flex items-center justify-between p-5 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
          <div className="flex items-center space-x-5">
            <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
              <Wrench className="w-6 h-6 text-slate-600 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
            </div>
            <span className="text-lg text-slate-700 dark:text-slate-200 font-semibold">Create New Equipment</span>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-indigo-500 transition-colors" />
        </button>

        <button className="flex items-center justify-between p-5 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
          <div className="flex items-center space-x-5">
            <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
              <Edit className="w-6 h-6 text-slate-600 dark:text-slate-400 group-hover:text-amber-600" />
            </div>
            <span className="text-lg text-slate-700 dark:text-slate-200 font-semibold">View Recommended Proposals</span>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-indigo-500 transition-colors" />
        </button>

        <button className="flex items-center justify-between p-5 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
          <div className="flex items-center space-x-5">
            <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
              <Search className="w-6 h-6 text-slate-600 dark:text-slate-400 group-hover:text-emerald-600" />
            </div>
            <span className="text-lg text-slate-700 dark:text-slate-200 font-semibold">View Current Revisions</span>
          </div>
          <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-indigo-500 transition-colors" />
        </button>

      </div>
      
    </div>
  )
}
