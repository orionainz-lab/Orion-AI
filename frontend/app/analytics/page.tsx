/**
 * Analytics Page
 * Dashboard with performance metrics and insights
 */

'use client'

import { AppLayout } from '@/components/layout/AppLayout'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">
            Performance metrics and insights
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approval Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  70%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-sm text-green-600 mt-4">+5% from last week</p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  2.3s
                </p>
              </div>
              <Activity className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600 mt-4">Within target</p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rejection Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  11%
                </p>
              </div>
              <TrendingDown className="w-8 h-8 text-red-600" />
            </div>
            <p className="text-sm text-red-600 mt-4">-3% from last week</p>
          </div>
        </div>

        {/* Placeholder */}
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Coming Soon
          </h3>
          <p className="text-gray-600">
            Advanced analytics and visualizations will be available in Phase 4.3
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
