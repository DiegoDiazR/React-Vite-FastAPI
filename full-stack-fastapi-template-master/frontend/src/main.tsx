import { ThemeProvider } from "next-themes"
import React, { Suspense } from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import { AppRoutes } from "./app/routes/AppRoutes"
import "./index.css"
import "./i18n"

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Suspense fallback="Loading...">
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </Suspense>
  </React.StrictMode>,
)
