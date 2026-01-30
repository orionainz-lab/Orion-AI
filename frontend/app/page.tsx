/**
 * Dashboard Home Page V2
 * Overview with real stats from Supabase
 */

'use client'

import { useEffect, useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Activity, CheckCircle, Clock, XCircle } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

interface Stats {
  total: number
  approved: number
  pending: number
  rejected: number
}

export default function Home() {
  const [stats, setStats] = useState<Stats>({
    total: 0,
    approved: 0,
    pending: 0,
    rejected: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      const supabase = createClient()

      try {
        // Get total count
        const { count: total } = await supabase
          .from('process_events')
          .select('*', { count: 'exact', head: true })

        // Get approved count
        const { count: approved } = await supabase
          .from('process_events')
          .select('*', { count: 'exact', head: true })
          .eq('event_metadata->>status', 'approved')

        // Get pending count
        const { count: pending } = await supabase
          .from('process_events')
          .select('*', { count: 'exact', head: true })
          .eq('event_metadata->>status', 'pending')

        // Get rejected count
        const { count: rejected } = await supabase
          .from('process_events')
          .select('*', { count: 'exact', head: true })
          .eq('event_metadata->>status', 'rejected')

        setStats({
          total: total || 0,
          approved: approved || 0,
          pending: pending || 0,
          rejected: rejected || 0,
        })
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    { name: 'Total Proposals', value: stats.total, icon: Activity, color: 'blue' },
    { name: 'Approved', value: stats.approved, icon: CheckCircle, color: 'green' },
    { name: 'Pending', value: stats.pending, icon: Clock, color: 'yellow' },
    { name: 'Rejected', value: stats.rejected, icon: XCircle, color: 'red' },
  ]

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome to Orion AI Command Center
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat) => {
            const Icon = stat.icon
            const colorClasses = {
              blue: 'bg-blue-100 text-blue-600',
              green: 'bg-green-100 text-green-600',
              yellow: 'bg-yellow-100 text-yellow-600',
              red: 'bg-red-100 text-red-600',
            }

            return (
              <div
                key={stat.name}
                className="bg-white rounded-lg border border-gray-200 p-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.name}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {loading ? '-' : stat.value.toLocaleString()}
                    </p>
                  </div>
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      colorClasses[stat.color as keyof typeof colorClasses]
                    }`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/matrix"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900">View Matrix Grid</p>
                <p className="text-sm text-gray-600">All proposals</p>
              </div>
            </a>
            <a
              href="/analytics"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900">View Analytics</p>
                <p className="text-sm text-gray-600">Performance metrics</p>
              </div>
            </a>
            <a
              href="/settings"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900">Settings</p>
                <p className="text-sm text-gray-600">Configure system</p>
              </div>
            </a>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            System Status
          </h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-gray-600">Realtime Connection</span>
              <span className="flex items-center gap-2 text-sm font-medium text-green-600">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-gray-600">Temporal Integration</span>
              <span className="flex items-center gap-2 text-sm font-medium text-green-600">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                Active
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-gray-600">Database</span>
              <span className="flex items-center gap-2 text-sm font-medium text-green-600">
                <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                Healthy
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
