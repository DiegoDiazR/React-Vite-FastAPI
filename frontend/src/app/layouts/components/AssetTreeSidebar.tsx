import { useState } from "react"
import { ChevronRight, ChevronDown, MapPin, Factory, FolderClosed, Package, Search } from "lucide-react"

type TreeNode = {
  id: string
  name: string
  type: "site" | "facility" | "folder" | "item"
  children?: TreeNode[]
}

const DUMMY_TREE: TreeNode[] = [
  {
    id: "1",
    name: "Cusiana",
    type: "site",
    children: [
      {
        id: "1-1",
        name: "CPF Cusiana",
        type: "facility",
        children: [
          {
            id: "1-1-1",
            name: "5",
            type: "item"
          }
        ]
      }
    ]
  }
]

export const AssetTreeSidebar = () => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(["1", "1-1"]))

  const toggleExpand = (id: string) => {
    const newSet = new Set(expandedNodes)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setExpandedNodes(newSet)
  }

  const renderIcon = (type: string) => {
    switch (type) {
      case "site": return <MapPin className="w-4 h-4 text-red-500" />
      case "facility": return <Factory className="w-4 h-4 text-orange-600" />
      case "folder": return <FolderClosed className="w-4 h-4 text-yellow-500" />
      case "item": return <Package className="w-4 h-4 text-gray-500" />
      default: return <Package className="w-4 h-4 text-gray-500" />
    }
  }

  const renderTree = (nodes: TreeNode[], level = 0) => {
    return nodes.map(node => {
      const isExpanded = expandedNodes.has(node.id)
      const hasChildren = node.children && node.children.length > 0

      return (
        <div key={node.id} className="flex flex-col">
          <div 
            className="flex items-center px-2 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
            style={{ paddingLeft: `${level * 16 + 12}px` }}
            onClick={() => hasChildren && toggleExpand(node.id)}
          >
            <div className="w-4 h-4 mr-2 flex items-center justify-center">
              {hasChildren && (
                isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />
              )}
            </div>
            <div className="mr-2 flex-shrink-0">
              {renderIcon(node.type)}
            </div>
            <span className="text-[13px] text-slate-700 dark:text-slate-300 truncate">{node.name}</span>
          </div>
          {isExpanded && hasChildren && (
            <div className="flex flex-col w-full">
              {renderTree(node.children!, level + 1)}
            </div>
          )}
        </div>
      )
    })
  }

  return (
    <div className="w-60 h-full border-r border-slate-200 dark:border-slate-800 bg-[#f8fafc] dark:bg-slate-900 flex flex-col shrink-0">
      {/* Header */}
      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 border-b border-slate-200 dark:border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Asset Explorer
      </div>
      
      {/* Search Bar */}
      <div className="p-3 border-b border-slate-100 dark:border-slate-800">
        <div className="relative">
          <input 
            type="text" 
            placeholder="Search assets..." 
            className="w-full text-xs py-1.5 px-3 pr-8 border border-slate-200 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow"
          />
          <Search className="w-3.5 h-3.5 absolute right-2.5 top-2 text-slate-400" />
        </div>
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto py-3">
        {renderTree(DUMMY_TREE)}
      </div>
    </div>
  )
}
