import { NavLink } from "react-router-dom"
import { 
  Home, Edit, Search, FileText, CalendarClock, 
  CalendarDays, Archive 
} from "lucide-react"

export const MiddleMenuSidebar = () => {
  const menuItems = [
    { label: "Home", icon: Home, to: "/" },
    { label: "Recommended Proposals", icon: Edit, to: "/proposals" },
    { label: "Current Revisions", icon: Search, to: "/revisions" },
    { label: "Risk Analysis FC", icon: FileText, to: "/risk-fc", color: "text-blue-500" },
    { label: "Risk Analysis CA", icon: FileText, to: "/risk-ca", color: "text-red-500" },
    { label: "Inspection / Mitigation Planning", icon: CalendarClock, to: "/planning", color: "text-orange-500" },
    { label: "Inspection / Mitigation Schedule", icon: CalendarDays, to: "/schedule", color: "text-green-500" },
    { label: "Archived Equipment Records", icon: Archive, to: "/archives", bg: "bg-slate-100 dark:bg-slate-800" },
  ]

  return (
    <div className="w-64 h-full border-r border-slate-200 dark:border-slate-800 bg-[#f8fafc] dark:bg-slate-900 flex flex-col shrink-0">
      {/* Header */}
      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 border-b border-slate-200 dark:border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Navigation Menu
      </div>
      
      {/* Menu Items */}
      <div className="flex-1 overflow-y-auto py-4 space-y-1">
        {menuItems.map((item, index) => (
          <NavLink
            key={index}
            to={item.to}
            className={({ isActive }) => 
              `flex items-center px-4 py-2.5 mx-2 rounded-lg transition-all duration-200 group ${
                isActive 
                  ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 font-semibold shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
              }`
            }
          >
            <item.icon className={`w-5 h-5 mr-3 transition-colors ${
              item.color || 'text-slate-400 group-hover:text-indigo-500'
            }`} />
            <span className="text-[13px]">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </div>
  )
}
