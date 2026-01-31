/**
 * Connector Marketplace Page
 * Browse and install connectors from the marketplace
 */

'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { ConnectorCard, InstallModal } from '@/components/marketplace'
import { Search, Package, TrendingUp, Star } from 'lucide-react'
import type { ConnectorMarketplace } from '@/types/database'

interface MarketplaceConnector {
  id: string
  name: string
  description: string | null
  category: string
  rating: number | null
  installCount: number
  isVerified: boolean
  publisher: string
  pricingModel: 'free' | 'paid' | 'freemium'
}

const categories = [
  { id: 'all', name: 'All Connectors', icon: Package },
  { id: 'crm', name: 'CRM', icon: TrendingUp },
  { id: 'accounting', name: 'Accounting', icon: Package },
  { id: 'communication', name: 'Communication', icon: Package },
  { id: 'custom', name: 'Custom', icon: Package }
]

export default function MarketplacePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedConnector, setSelectedConnector] = useState<MarketplaceConnector | null>(null)
  const [isInstallModalOpen, setIsInstallModalOpen] = useState(false)
  const [connectors, setConnectors] = useState<MarketplaceConnector[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch connectors from API
  useEffect(() => {
    async function fetchConnectors() {
      try {
        const response = await fetch('/api/marketplace')
        if (!response.ok) throw new Error('Failed to fetch connectors')
        
        const data = await response.json()
        const formattedConnectors: MarketplaceConnector[] = data.connectors.map((c: ConnectorMarketplace) => ({
          id: c.id,
          name: c.name,
          description: c.description,
          category: c.category,
          rating: c.rating ? parseFloat(c.rating.toString()) : null,
          installCount: c.install_count || 0,
          isVerified: c.is_verified || false,
          publisher: c.is_verified ? 'Orion AI Official' : 'Community',
          pricingModel: c.pricing_model || 'free'
        }))
        
        setConnectors(formattedConnectors)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load connectors')
        setLoading(false)
      }
    }

    fetchConnectors()
  }, [])

  const filteredConnectors = connectors.filter(connector => {
    const matchesSearch = connector.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (connector.description?.toLowerCase() || '').includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || connector.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleInstall = (connectorId: string) => {
    const connector = connectors.find(c => c.id === connectorId)
    if (connector) {
      setSelectedConnector(connector)
      setIsInstallModalOpen(true)
    }
  }

  const handleInstallConfirm = (connectorId: string, config: Record<string, string>) => {
    console.log('Installing connector:', connectorId, config)
    // Handle actual installation logic here
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading connectors...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error) {
    return (
      <AppLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error}</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Connector Marketplace</h1>
          <p className="text-gray-600 mt-1">
            Browse and install connectors to integrate with your favorite apps
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center space-x-2">
              <Package className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{connectors.length}</p>
                <p className="text-sm text-gray-600">Available Connectors</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center space-x-2">
              <Star className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {connectors.filter(c => c.isVerified).length}
                </p>
                <p className="text-sm text-gray-600">Verified Connectors</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {connectors.reduce((sum, c) => sum + c.installCount, 0).toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">Total Installs</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search connectors..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-2 md:pb-0">
            {categories.map((category) => {
              const Icon = category.icon
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{category.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Connectors Grid */}
        {filteredConnectors.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredConnectors.map((connector) => (
              <ConnectorCard
                key={connector.id}
                connector={connector}
                onInstall={handleInstall}
                onViewDetails={(id) => console.log('View details:', id)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No connectors found
            </h3>
            <p className="text-gray-600">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}

        {/* Build Your Own CTA */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="mb-4 md:mb-0">
              <h3 className="text-xl font-semibold mb-2">Can&apos;t find what you&apos;re looking for?</h3>
              <p className="text-blue-100">
                Build your own custom connector with our AI-powered builder - no coding required!
              </p>
            </div>
            <a
              href="/connectors/builder"
              className="px-6 py-3 bg-white text-blue-600 font-medium rounded-lg hover:bg-gray-100 transition-colors"
            >
              Build Custom Connector
            </a>
          </div>
        </div>
      </div>

      {/* Install Modal */}
      {selectedConnector && (
        <InstallModal
          connector={selectedConnector}
          isOpen={isInstallModalOpen}
          onClose={() => setIsInstallModalOpen(false)}
          onInstall={handleInstallConfirm}
        />
      )}
    </AppLayout>
  )
}
