/**
 * Top Connectors List
 * Shows the most active connectors
 */

'use client'

import { Database, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'

interface Connector {
  name: string
  records: number
  status: 'healthy' | 'degraded' | 'failed'
  lastSync?: string
}

interface TopConnectorsProps {
  connectors: Connector[]
  onConnectorClick?: (connectorName: string) => void
}

export function TopConnectors({ connectors, onConnectorClick }: TopConnectorsProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="w-4 h-4 text-green-600" />
      case 'degraded': return <AlertTriangle className="w-4 h-4 text-yellow-600" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />
      default: return <Database className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      healthy: 'bg-green-100 text-green-700',
      degraded: 'bg-yellow-100 text-yellow-700',
      failed: 'bg-red-100 text-red-700'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Top Connectors</h3>
        <Database className="w-5 h-5 text-gray-500" />
      </div>

      <div className="space-y-3">
        {connectors.map((connector, index) => (
          <div 
            key={connector.name}
            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
            onClick={() => onConnectorClick?.(connector.name)}
          >
            <div className="flex items-center space-x-3 flex-1">
              <span className="text-sm font-medium text-gray-500 w-6">#{index + 1}</span>
              {getStatusIcon(connector.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{connector.name}</p>
                {connector.lastSync && (
                  <p className="text-xs text-gray-500">Last sync: {connector.lastSync}</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm font-bold text-gray-900">{connector.records.toLocaleString()}</span>
              <span className={`text-xs px-2 py-1 rounded-full ${getStatusBadge(connector.status)}`}>
                {connector.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {connectors.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No active connectors</p>
        </div>
      )}
    </div>
  )
}
