'use client'

/**
 * Application Layout Wrapper
 * Contains header, sidebar, and main content area
 */

import { useState } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { NotificationToast } from '@/components/ui/NotificationToast'
import { ProposalModal } from '@/components/ui/ProposalModal'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(true)} />

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>

      {/* Notification Toasts */}
      <NotificationToast />

      {/* Proposal Modal */}
      <ProposalModal />
    </div>
  )
}
