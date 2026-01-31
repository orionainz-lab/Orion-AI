/**
 * Analytics Page
 * Real-time dashboard with connector metrics and performance insights
 */

'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { ConnectorHealth, SyncMetrics, PerformanceMetrics, TopConnectors } from '@/components/analytics'
import { LineChart, BarChart } from '@/components/charts'
import { Download } from 'lucide-react'

// Sample data for demonstration
const generateSyncTrendData = () => {
  const data = []
  const now = new Date()
  for (let i = 6; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      records: Math.floor(Math.random() * 2000) + 1000,
      syncs: Math.floor(Math.random() * 50) + 20
    })
  }
  return data
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d')
  const [syncTrendData] = useState(generateSyncTrendData())

  const topConnectors = [
    { name: 'Salesforce', records: 45678, status: 'healthy' as const, lastSync: '2 mins ago' },
    { name: 'HubSpot', records: 34567, status: 'healthy' as const, lastSync: '5 mins ago' },
    { name: 'Stripe', records: 23456, status: 'degraded' as const, lastSync: '15 mins ago' },
    { name: 'QuickBooks', records: 12345, status: 'healthy' as const, lastSync: '8 mins ago' },
    { name: 'Slack', records: 8901, status: 'healthy' as const, lastSync: '1 min ago' }
  ]

  const connectorDistribution = [
    { name: 'Salesforce', value: 45678 },
    { name: 'HubSpot', value: 34567 },
    { name: 'Stripe', value: 23456 },
    { name: 'QuickBooks', value: 12345 },
    { name: 'Slack', value: 8901 }
  ]

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600 mt-1">
              Real-time performance metrics and connector insights
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Time Range Selector */}
            <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200 p-1">
              {(['7d', '30d', '90d'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 text-sm rounded ${
                    timeRange === range
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
                </button>
              ))}
            </div>
            
            {/* Export Button */}
            <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Export</span>
            </button>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ConnectorHealth 
            healthy={25} 
            degraded={2} 
            failed={1}
            onViewDetails={(status) => console.log('View details:', status)}
          />
          
          <SyncMetrics 
            last24h={12456}
            last7d={87234}
            last30d={345678}
            successRate={98.5}
            trend="up"
            trendPercentage={5.2}
          />
          
          <PerformanceMetrics 
            avgResponseTime={234}
            p95ResponseTime={567}
            errorRate={1.5}
            successRate={98.5}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sync Volume Trend */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sync Volume Trend</h3>
            <LineChart 
              data={syncTrendData}
              xKey="date"
              lines={[
                { dataKey: 'records', name: 'Records Synced', color: '#3b82f6' },
                { dataKey: 'syncs', name: 'Sync Count', color: '#10b981' }
              ]}
              height={250}
            />
          </div>

          {/* Top Connectors */}
          <TopConnectors 
            connectors={topConnectors}
            onConnectorClick={(name) => console.log('View connector:', name)}
          />
        </div>

        {/* Connector Distribution */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Records by Connector</h3>
          <BarChart 
            data={connectorDistribution}
            xKey="name"
            bars={[
              { dataKey: 'value', name: 'Records', color: '#3b82f6' }
            ]}
            height={300}
          />
        </div>

        {/* Real-time Updates Footer */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-blue-900">Live data • Updated just now</span>
            </div>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View Historical Data
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
