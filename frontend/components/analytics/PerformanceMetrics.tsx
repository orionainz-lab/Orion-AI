/**
 * Performance Metrics Widget
 * Displays API performance statistics
 */

'use client'

import { Zap, Clock, AlertTriangle } from 'lucide-react'

interface PerformanceMetricsProps {
  avgResponseTime: number // in ms
  p95ResponseTime: number // in ms
  errorRate: number // percentage
  successRate: number // percentage
}

export function PerformanceMetrics({ 
  avgResponseTime, 
  p95ResponseTime, 
  errorRate,
  successRate 
}: PerformanceMetricsProps) {
  const getResponseTimeColor = (time: number) => {
    if (time < 500) return 'text-green-600'
    if (time < 1000) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getErrorRateColor = (rate: number) => {
    if (rate < 1) return 'text-green-600'
    if (rate < 5) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
        <Zap className="w-5 h-5 text-gray-500" />
      </div>

      <div className="space-y-4">
        {/* Avg Response Time */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Avg Response</span>
          </div>
          <span className={`text-xl font-bold ${getResponseTimeColor(avgResponseTime)}`}>
            {avgResponseTime}ms
          </span>
        </div>

        {/* P95 Response Time */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">P95 Response</span>
          </div>
          <span className={`text-xl font-bold ${getResponseTimeColor(p95ResponseTime)}`}>
            {p95ResponseTime}ms
          </span>
        </div>

        {/* Error Rate */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Error Rate</span>
          </div>
          <span className={`text-xl font-bold ${getErrorRateColor(errorRate)}`}>
            {errorRate.toFixed(2)}%
          </span>
        </div>

        {/* Success Rate */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Success Rate</span>
            <span className="text-2xl font-bold text-green-600">{successRate.toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
