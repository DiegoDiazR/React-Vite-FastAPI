import { Outlet } from "react-router-dom"
import { Header } from "../common/ui/Header"
import { Sidebar } from "../common/ui/Sidebar"

export const MainLayout = () => {
  return (
    <div className="flex h-screen bg-zinc-50 dark:bg-zinc-950 transition-colors">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Wrapper */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
