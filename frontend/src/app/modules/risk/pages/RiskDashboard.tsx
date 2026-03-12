import { Wrench, Edit, Search, ChevronRight } from "lucide-react"
import { RiskHeatMap } from "../components/RiskHeatMap"

const MOCK_RISK_ITEMS = [
  { id: '1', name: 'Pipe-001', probability: 4, consequence: 'D' },
  { id: '2', name: 'Tank-005', probability: 2, consequence: 'B' },
  { id: '3', name: 'Valve-221', probability: 5, consequence: 'E' },
  { id: '4', name: 'HeatEx-12', probability: 1, consequence: 'A' },
  { id: '5', name: 'Pipe-099', probability: 3, consequence: 'C' },
  { id: '6', name: 'Vessel-04', probability: 4, consequence: 'D' },
];

export const RiskDashboard = () => {

  return (
    <div className="flex flex-col lg:flex-row h-full w-full bg-[#f8fafc] dark:bg-slate-950 p-8 lg:p-12 overflow-y-auto">
      
      {/* Left Section: Welcome & Actions */}
      <div className="flex flex-col flex-1 items-start justify-center lg:pr-12 mb-12 lg:mb-0">
        
        {/* Logo/Title Area */}
        <div className="flex items-center space-x-3 mb-8">
          <h1 className="text-4xl font-light text-slate-900 dark:text-slate-100 tracking-tight">
            CoreRisk <sup className="text-xs text-indigo-600 font-bold">®</sup>
          </h1>
          <div className="w-12 h-12 rounded-2xl bg-indigo-700 dark:bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-xl rotate-3">
            C
          </div>
        </div>

        <div className="mb-10">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">Welcome back, Engineer</h2>
          <p className="text-slate-500 dark:text-slate-400">Manage your assets and analyze risks using API 581 standards.</p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col space-y-4 w-full max-w-md">
          
          <button className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
                <Wrench className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
              </div>
              <span className="text-base text-slate-700 dark:text-slate-200 font-semibold text-left">Create New Equipment</span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
          </button>

          <button className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
                <Edit className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600" />
              </div>
              <span className="text-base text-slate-700 dark:text-slate-200 font-semibold text-left">View Recommended Proposals</span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
          </button>

          <button className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md transition-all group">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors">
                <Search className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-emerald-600" />
              </div>
              <span className="text-base text-slate-700 dark:text-slate-200 font-semibold text-left">View Current Revisions</span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
          </button>

        </div>
      </div>

      {/* Right Section: Visual Analytics */}
      <div className="flex-1 flex flex-col items-center justify-center space-y-8 h-full bg-slate-50/50 dark:bg-slate-900/50 rounded-3xl p-8 border border-slate-200 dark:border-slate-800">
        <div className="w-full text-center mb-4">
          <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold rounded-full uppercase tracking-widest">
            Live Risk Overview
          </span>
        </div>
        
        <RiskHeatMap items={MOCK_RISK_ITEMS} />
        
        <div className="grid grid-cols-2 gap-4 w-full max-w-sm">
           <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
             <div className="text-2xl font-bold text-indigo-600">84</div>
             <div className="text-[10px] text-slate-400 font-bold uppercase">Total Assets</div>
           </div>
           <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
             <div className="text-2xl font-bold text-rose-500">12</div>
             <div className="text-[10px] text-slate-400 font-bold uppercase">High Risk</div>
           </div>
        </div>
      </div>
      
    </div>
  );
}
