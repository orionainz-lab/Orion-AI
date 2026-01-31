/**
 * Connector Health Widget
 * Displays real-time connector status
 */

'use client'

import { Activity, AlertCircle, CheckCircle2, XCircle } from 'lucide-react'

interface ConnectorHealthProps {
  healthy: number
  degraded: number
  failed: number
  onViewDetails?: (status: string) => void
}

export function ConnectorHealth({ healthy, degraded, failed, onViewDetails }: ConnectorHealthProps) {
  const total = healthy + degraded + failed

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Connector Health</h3>
        <Activity className="w-5 h-5 text-gray-500" />
      </div>

      <div className="space-y-3">
        {/* Healthy */}
        <div 
          className="flex items-center justify-between p-3 rounded-lg bg-green-50 cursor-pointer hover:bg-green-100 transition-colors"
          onClick={() => onViewDetails?.('healthy')}
        >
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Healthy</span>
          </div>
          <span className="text-2xl font-bold text-green-600">{healthy}</span>
        </div>

        {/* Degraded */}
        <div 
          className="flex items-center justify-between p-3 rounded-lg bg-yellow-50 cursor-pointer hover:bg-yellow-100 transition-colors"
          onClick={() => onViewDetails?.('degraded')}
        >
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-gray-700">Degraded</span>
          </div>
          <span className="text-2xl font-bold text-yellow-600">{degraded}</span>
        </div>

        {/* Failed */}
        <div 
          className="flex items-center justify-between p-3 rounded-lg bg-red-50 cursor-pointer hover:bg-red-100 transition-colors"
          onClick={() => onViewDetails?.('failed')}
        >
          <div className="flex items-center space-x-3">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-sm font-medium text-gray-700">Failed</span>
          </div>
          <span className="text-2xl font-bold text-red-600">{failed}</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Total Connectors</span>
          <span className="font-semibold text-gray-900">{total}</span>
        </div>
      </div>
    </div>
  )
}
