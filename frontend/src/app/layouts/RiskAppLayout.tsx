import { Outlet } from "react-router-dom"
import { RibbonTopbar } from "./components/RibbonTopbar"
import { AssetTreeSidebar } from "./components/AssetTreeSidebar"
import { MiddleMenuSidebar } from "./components/MiddleMenuSidebar"

export const RiskAppLayout = () => {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-white dark:bg-zinc-950 text-slate-900 dark:text-slate-100 font-sans">
      {/* Top Ribbon Navigation */}
      <RibbonTopbar />

      {/* Main Two-Panel Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Leftmost Asset Tree */}
        <AssetTreeSidebar />

        {/* Middle Navigation Menu */}
        <MiddleMenuSidebar />

        {/* Dynamic Content Area (Start Screen, Grids, Modals, etc.) */}
        <div className="flex-1 flex flex-col overflow-hidden bg-white dark:bg-slate-950 relative">
          <Outlet />
        </div>
      </div>
      
      {/* Footer / Status Bar */}
      <div className="h-6 flex items-center justify-between px-2 bg-[#f0f0f0] dark:bg-slate-800 border-t border-slate-300 dark:border-slate-700 text-[10px] text-slate-600 dark:text-slate-400">
        <div className="flex items-center space-x-4">
          <span>User: Admin User</span>
          <span>Application: CoreRisk</span>
          <span>Server: Localhost</span>
        </div>
      </div>
    </div>
  )
}
