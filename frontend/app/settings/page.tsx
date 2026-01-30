/**
 * Settings Page
 * System configuration and preferences
 */

'use client'

import { AppLayout } from '@/components/layout/AppLayout'
import { Settings as SettingsIcon } from 'lucide-react'

export default function SettingsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Configure your system preferences
          </p>
        </div>

        {/* Placeholder */}
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <SettingsIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Coming Soon
          </h3>
          <p className="text-gray-600">
            Settings and configuration options will be available in Phase 4.3
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
