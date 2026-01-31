/**
 * Connector Card Component
 * Display individual connector in marketplace
 */

'use client'

import { Star, Download, Shield } from 'lucide-react'

interface ConnectorCardProps {
  connector: {
    id: string
    name: string
    description: string
    category: string
    rating: number
    installCount: number
    isVerified: boolean
    publisher: string
    pricingModel: 'free' | 'paid' | 'freemium'
  }
  onInstall?: (connectorId: string) => void
  onViewDetails?: (connectorId: string) => void
}

export function ConnectorCard({ connector, onInstall, onViewDetails }: ConnectorCardProps) {
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      crm: 'bg-blue-100 text-blue-700',
      accounting: 'bg-green-100 text-green-700',
      communication: 'bg-purple-100 text-purple-700',
      marketing: 'bg-pink-100 text-pink-700',
      custom: 'bg-gray-100 text-gray-700'
    }
    return colors[category] || colors.custom
  }

  const getPricingBadge = (model: string) => {
    const badges: Record<string, { text: string; color: string }> = {
      free: { text: 'Free', color: 'bg-green-100 text-green-700' },
      paid: { text: 'Paid', color: 'bg-blue-100 text-blue-700' },
      freemium: { text: 'Freemium', color: 'bg-purple-100 text-purple-700' }
    }
    return badges[model] || badges.free
  }

  const pricing = getPricingBadge(connector.pricingModel)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900">{connector.name}</h3>
            {connector.isVerified && (
              <Shield className="w-4 h-4 text-blue-600" title="Verified connector" />
            )}
          </div>
          <p className="text-xs text-gray-500">by {connector.publisher}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${pricing.color}`}>
          {pricing.text}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {connector.description}
      </p>

      {/* Metadata */}
      <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600">
        {/* Rating */}
        <div className="flex items-center space-x-1">
          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          <span className="font-medium">{connector.rating.toFixed(1)}</span>
        </div>

        {/* Installs */}
        <div className="flex items-center space-x-1">
          <Download className="w-4 h-4" />
          <span>{connector.installCount.toLocaleString()}</span>
        </div>

        {/* Category */}
        <span className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(connector.category)}`}>
          {connector.category}
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onInstall?.(connector.id)
          }}
          className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          Install
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onViewDetails?.(connector.id)
          }}
          className="px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
        >
          Details
        </button>
      </div>
    </div>
  )
}
