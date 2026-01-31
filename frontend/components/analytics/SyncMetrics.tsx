/**
 * Sync Metrics Widget
 * Displays sync statistics and trends
 */

'use client'

import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'

interface SyncMetricsProps {
  last24h: number
  last7d: number
  last30d: number
  successRate: number
  trend: 'up' | 'down' | 'stable'
  trendPercentage: number
}

export function SyncMetrics({ 
  last24h, 
  last7d, 
  last30d, 
  successRate, 
  trend,
  trendPercentage 
}: SyncMetricsProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Sync Metrics</h3>
        <RefreshCw className="w-5 h-5 text-gray-500" />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        {/* Last 24h */}
        <div>
          <p className="text-xs text-gray-500 mb-1">Last 24h</p>
          <p className="text-2xl font-bold text-gray-900">{last24h.toLocaleString()}</p>
        </div>

        {/* Last 7d */}
        <div>
          <p className="text-xs text-gray-500 mb-1">Last 7 days</p>
          <p className="text-2xl font-bold text-gray-900">{last7d.toLocaleString()}</p>
        </div>

        {/* Last 30d */}
        <div>
          <p className="text-xs text-gray-500 mb-1">Last 30 days</p>
          <p className="text-2xl font-bold text-gray-900">{last30d.toLocaleString()}</p>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Success Rate</span>
          <span className="text-lg font-bold text-gray-900">{successRate.toFixed(1)}%</span>
        </div>
        
        {trend !== 'stable' && (
          <div className={`flex items-center text-sm ${trendColor}`}>
            <TrendIcon className="w-4 h-4 mr-1" />
            <span>{Math.abs(trendPercentage).toFixed(1)}% from last week</span>
          </div>
        )}
      </div>
    </div>
  )
}
