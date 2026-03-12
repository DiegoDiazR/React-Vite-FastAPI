import { useState } from "react"
import { NavLink } from "react-router-dom"
import { 
  FilePlus, Save, MapPin, Factory, Users, 
  BookOpen, Droplets, HardHat, 
  Activity, FileText
} from "lucide-react"

export const RibbonTopbar = () => {
  const [activeTab, setActiveTab] = useState("Components")

  const tabs = ["Settings", "Tools", "Components", "Help"]

  const RibbonButton = ({ icon: Icon, label, disabled = false }: { icon: any, label: string, disabled?: boolean }) => (
    <button 
      disabled={disabled}
      className={`flex flex-col items-center justify-center p-2 min-w-[70px] hover:bg-indigo-50 dark:hover:bg-indigo-900/40 rounded border border-transparent hover:border-indigo-200 dark:hover:border-indigo-800 transition-colors ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <Icon className="w-8 h-8 mb-1 text-slate-700 dark:text-slate-300" />
      <span className="text-xs text-center leading-tight truncate w-full text-slate-600 dark:text-slate-400">{label}</span>
    </button>
  )

  const Separator = () => (
    <div className="w-px h-16 bg-slate-200 dark:bg-slate-700 mx-1"></div>
  )

  return (
    <div className="flex flex-col w-full bg-[#f8fafc] dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm">
      {/* Tab headers */}
      <div className="flex space-x-1 px-4 pt-1.5 flex-1">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 text-xs font-semibold rounded-t-md transition-all ${
              activeTab === tab 
                ? "bg-white dark:bg-slate-800 text-indigo-700 dark:text-indigo-400 border-x border-t border-slate-200 dark:border-slate-700 relative top-[1px]" 
                : "bg-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            }`}
            style={{ zIndex: activeTab === tab ? 10 : 1 }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Ribbon Body */}
      <div className="flex items-center p-2 min-h-[95px] bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 relative z-[5]">
        {activeTab === "Components" ? (
          <div className="flex items-center space-x-1">
            <div className="flex flex-col items-center justify-center">
              <div className="flex space-x-1">
                <RibbonButton icon={FilePlus} label="New" disabled />
                <RibbonButton icon={Save} label="Save" disabled />
              </div>
              <span className="text-[10px] text-slate-400 mt-1 uppercase">File</span>
            </div>
            
            <Separator />

            <div className="flex flex-col items-center justify-center">
              <div className="flex space-x-1">
                <RibbonButton icon={MapPin} label="Sites" />
                <RibbonButton icon={Factory} label="Facilities" />
                <RibbonButton icon={Users} label="Manufacturers" />
                <RibbonButton icon={BookOpen} label="Design Codes" />
                <NavLink to="/generic-fluids">
                  <RibbonButton icon={Droplets} label="Generic Fluids" />
                </NavLink>
                <RibbonButton icon={HardHat} label="Generic Materials" />
              </div>
              <span className="text-[10px] text-slate-400 mt-1 uppercase">Component Properties</span>
            </div>
          </div>
        ) : activeTab === "Tools" ? (
          <div className="flex items-center space-x-1">
             <div className="flex flex-col items-center justify-center">
              <div className="flex space-x-1">
                <RibbonButton icon={FilePlus} label="New" disabled />
                <RibbonButton icon={Save} label="Save" disabled />
              </div>
              <span className="text-[10px] text-slate-400 mt-1 uppercase">File</span>
            </div>

            <Separator />

            <div className="flex flex-col items-center justify-center">
              <div className="flex space-x-1">
                <RibbonButton icon={Activity} label="Calculator" />
                <RibbonButton icon={FileText} label="Notepad" />
              </div>
              <span className="text-[10px] text-slate-400 mt-1 uppercase">External Tools</span>
            </div>

            <Separator />

            <div className="flex flex-col items-center justify-center">
              <div className="flex space-x-1">
                <NavLink to="/import-preview">
                  <RibbonButton icon={FilePlus} label="Import Items Template" />
                </NavLink>
                <RibbonButton icon={FileText} label="Import Inspections Template" />
                <RibbonButton icon={Save} label="Import Inspections" disabled />
                <RibbonButton icon={FileText} label="Delete All Imported Records" disabled />
              </div>
              <span className="text-[10px] text-slate-400 mt-1 uppercase">Database Utilities</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center text-slate-500 italic px-4">
            (Options for {activeTab} are currently empty in this template)
          </div>
        )}
      </div>
    </div>
  )
}
