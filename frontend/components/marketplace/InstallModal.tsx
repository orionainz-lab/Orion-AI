/**
 * Install Modal Component
 * Configure and install connector from marketplace
 */

'use client'

import { useState } from 'react'
import { X, Check, AlertCircle } from 'lucide-react'

interface InstallModalProps {
  connector: {
    id: string
    name: string
    description: string
    category: string
  }
  isOpen: boolean
  onClose: () => void
  onInstall: (connectorId: string, config: Record<string, string>) => void
}

export function InstallModal({ connector, isOpen, onClose, onInstall }: InstallModalProps) {
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [isInstalling, setIsInstalling] = useState(false)

  if (!isOpen) return null

  const handleInstall = async () => {
    setIsInstalling(true)
    
    // Simulate installation
    setTimeout(() => {
      onInstall(connector.id, { apiKey, baseUrl })
      setIsInstalling(false)
      onClose()
    }, 1500)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Install {connector.name}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Configure connection settings
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Info Banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5" />
              <p className="text-xs text-blue-900">
                Your credentials are encrypted and stored securely. We never share your data with third parties.
              </p>
            </div>
          </div>

          {/* Description */}
          <div>
            <p className="text-sm text-gray-600">
              {connector.description}
            </p>
          </div>

          {/* Configuration Fields */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Base URL
            </label>
            <input
              type="url"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://api.example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isInstalling}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API key"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isInstalling}
            />
            <p className="mt-1 text-xs text-gray-500">
              Find your API key in {connector.name} settings
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            disabled={isInstalling}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleInstall}
            disabled={!apiKey || !baseUrl || isInstalling}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isInstalling ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Installing...</span>
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                <span>Install Connector</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
