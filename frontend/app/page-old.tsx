/**
 * Dashboard Home Page
 * Overview and quick stats
 */

'use client'

import { AppLayout } from '@/components/layout/AppLayout'
import { Activity, CheckCircle, Clock, XCircle } from 'lucide-react'

export default function Home() {
  const stats = [
    { name: 'Total Proposals', value: '127', icon: Activity, color: 'blue' },
    { name: 'Approved', value: '89', icon: CheckCircle, color: 'green' },
    { name: 'Pending', value: '24', icon: Clock, color: 'yellow' },
    { name: 'Rejected', value: '14', icon: XCircle, color: 'red' },
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
          {stats.map((stat) => {
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
                      {stat.value}
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

        {/* Recent Activity */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {[
              {
                action: 'Code generation approved',
                user: 'john@example.com',
                time: '2 minutes ago',
                status: 'approved',
              },
              {
                action: 'Workflow started',
                user: 'sarah@example.com',
                time: '5 minutes ago',
                status: 'pending',
              },
              {
                action: 'Code review rejected',
                user: 'mike@example.com',
                time: '10 minutes ago',
                status: 'rejected',
              },
            ].map((activity, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
              >
                <div>
                  <p className="font-medium text-gray-900">{activity.action}</p>
                  <p className="text-sm text-gray-600">
                    by {activity.user} · {activity.time}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    activity.status === 'approved'
                      ? 'bg-green-100 text-green-700'
                      : activity.status === 'pending'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
