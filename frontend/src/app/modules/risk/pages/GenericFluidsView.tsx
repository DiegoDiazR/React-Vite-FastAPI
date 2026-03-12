import { useState } from "react"
import { RefreshCw, Plus } from "lucide-react"

type FluidData = {
  fluid: string
  boilingPoint: number
  density: number
  mw: number
  chemicalFactor: number
  healthDegree: number
  flammability: number
  reactivity: number
  applyPrimary: boolean
  applyVolatile: boolean
}

const DUMMY_FLUIDS: FluidData[] = [
  { fluid: "Water", boilingPoint: 100, density: 1000, mw: 18.01, chemicalFactor: 1, healthDegree: 0, flammability: 0, reactivity: 0, applyPrimary: true, applyVolatile: false },
  { fluid: "Methane", boilingPoint: -161.5, density: 0.656, mw: 16.04, chemicalFactor: 2, healthDegree: 1, flammability: 4, reactivity: 0, applyPrimary: true, applyVolatile: true },
  { fluid: "Butane", boilingPoint: -1, density: 2.48, mw: 58.12, chemicalFactor: 2.2, healthDegree: 1, flammability: 4, reactivity: 0, applyPrimary: false, applyVolatile: true },
]

export const GenericFluidsView = () => {
  const [data] = useState<FluidData[]>(DUMMY_FLUIDS)

  return (
    <div className="flex flex-col h-full bg-[#f8fafc] dark:bg-slate-900 p-6">
      <div className="bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 rounded-xl flex flex-col h-full overflow-hidden">
        
        {/* Header from screenshot 2 */}
        <div className="bg-white dark:bg-slate-800 p-5 border-b border-slate-200 dark:border-slate-700 flex items-center shadow-sm z-10">
          <div className="flex items-center space-x-4">
             <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl text-indigo-600 dark:text-indigo-400">
               {/* Simplified icon representing the generic fluids icon */}
               <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                 <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
               </svg>
             </div>
             <div>
               <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Generic Fluids</h2>
               <p className="text-sm text-slate-500 dark:text-slate-400">Manage and configure system-wide fluid properties</p>
             </div>
          </div>
        </div>

        {/* Content Table */}
        <div className="flex-1 overflow-auto bg-white dark:bg-slate-900">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700 border-collapse">
            <thead className="bg-slate-50 dark:bg-slate-800/80 sticky top-0 z-10 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-left text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Fluid
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Boiling Point (°C)
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Density (kg/m³)
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  MW
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Chem Factor
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Health
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Flam.
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  React.
                </th>
                <th className="px-4 py-3.5 border-r border-slate-100 dark:border-slate-700 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Apply Primary
                </th>
                <th className="px-4 py-3.5 text-center text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider whitespace-nowrap">
                  Apply Volatile
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-100 dark:divide-slate-700">
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors">
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-slate-100">{row.fluid}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.boilingPoint}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.density}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.mw}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.chemicalFactor}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.healthDegree}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.flammability}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center text-slate-600 dark:text-slate-300">{row.reactivity}</td>
                  <td className="px-4 py-3 border-r border-slate-50 dark:border-slate-700 whitespace-nowrap text-sm text-center">
                    <input type="checkbox" checked={row.applyPrimary} readOnly className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500" />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                    <input type="checkbox" checked={row.applyVolatile} readOnly className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer Actions */}
        <div className="bg-slate-50 dark:bg-slate-800/80 p-4 border-t border-slate-200 dark:border-slate-700 flex justify-between items-center z-10">
          <div className="flex space-x-3">
            <button className="flex items-center px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm text-sm font-semibold transition-all">
              <Plus className="w-4 h-4 mr-2" />
              Add Fluid
            </button>
            <button className="flex items-center px-5 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg shadow-sm hover:bg-slate-50 dark:hover:bg-slate-600 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-all">
              <RefreshCw className="w-4 h-4 mr-2 text-indigo-500" />
              Refresh
            </button>
          </div>
          <button className="px-6 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg shadow-sm hover:bg-slate-50 dark:hover:bg-slate-600 text-sm font-semibold text-slate-700 dark:text-slate-200 transition-all">
            Close
          </button>
        </div>

      </div>
    </div>
  )
}
