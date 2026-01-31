/**
 * Test Sandbox Component
 * Test custom connector with sandbox credentials
 */

'use client'

import { useState } from 'react'
import { Play, CheckCircle2, XCircle, Loader2, Code } from 'lucide-react'

interface TestResult {
  success: boolean
  message: string
  data?: Array<{id: string; name: string}>
  error?: string
}

interface TestSandboxProps {
  connectorName?: string
  onTestComplete?: (result: TestResult) => void
}

export function TestSandbox({ connectorName = 'Custom Connector', onTestComplete }: TestSandboxProps) {
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [showLogs, setShowLogs] = useState(false)

  const handleTest = async () => {
    if (!apiKey || !baseUrl) return

    setIsTesting(true)
    setTestResult(null)

    // Simulate API test
    setTimeout(() => {
      const result: TestResult = {
        success: Math.random() > 0.3,
        message: Math.random() > 0.3 
          ? 'Connection successful! Retrieved 5 sample records.'
          : 'Connection failed: Invalid API key or endpoint.',
        data: Math.random() > 0.3 ? [
          { id: '1', name: 'Test Customer 1' },
          { id: '2', name: 'Test Customer 2' }
        ] : undefined,
        error: Math.random() > 0.3 ? undefined : '401 Unauthorized'
      }
      
      setTestResult(result)
      setIsTesting(false)
      onTestComplete?.(result)
    }, 2500)
  }

  const logs = [
    '[INFO] Initializing connector: ' + connectorName,
    '[INFO] Validating credentials...',
    '[INFO] Establishing connection to ' + baseUrl,
    testResult?.success 
      ? '[SUCCESS] Connection established successfully'
      : '[ERROR] Connection failed: Invalid credentials',
    testResult?.success 
      ? '[INFO] Fetching sample data...'
      : '[ERROR] Unable to authenticate',
    testResult?.success 
      ? '[SUCCESS] Retrieved 5 records'
      : ''
  ].filter(Boolean)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Play className="w-5 h-5 text-green-600" />
        <h3 className="text-lg font-semibold text-gray-900">Test Sandbox</h3>
      </div>

      <p className="text-sm text-gray-600 mb-6">
        Test your connector with sandbox credentials before deployment
      </p>

      <div className="space-y-4">
        {/* Base URL */}
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
            disabled={isTesting}
          />
        </div>

        {/* API Key */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key (Sandbox)
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk_test_..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isTesting}
          />
          <p className="mt-1 text-xs text-gray-500">
            Use test/sandbox credentials only
          </p>
        </div>

        {/* Test Button */}
        <button
          onClick={handleTest}
          disabled={!apiKey || !baseUrl || isTesting}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isTesting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Testing Connection...</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Run Test</span>
            </>
          )}
        </button>

        {/* Test Result */}
        {testResult && (
          <div className={`p-4 rounded-lg border-2 ${
            testResult.success 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-start space-x-2">
              {testResult.success ? (
                <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
              )}
              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  testResult.success ? 'text-green-900' : 'text-red-900'
                }`}>
                  {testResult.message}
                </p>
                
                {testResult.data && (
                  <div className="mt-3">
                    <button
                      onClick={() => setShowLogs(!showLogs)}
                      className="flex items-center space-x-1 text-xs text-green-700 hover:text-green-800"
                    >
                      <Code className="w-3 h-3" />
                      <span>{showLogs ? 'Hide' : 'Show'} Sample Data</span>
                    </button>
                    {showLogs && (
                      <pre className="mt-2 p-2 bg-white rounded text-xs overflow-auto border border-green-200">
                        {JSON.stringify(testResult.data, null, 2)}
                      </pre>
                    )}
                  </div>
                )}

                {testResult.error && (
                  <p className="mt-2 text-xs text-red-700 font-mono">
                    Error: {testResult.error}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Logs */}
        {(isTesting || testResult) && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Test Logs</span>
              <Code className="w-4 h-4 text-gray-400" />
            </div>
            <div className="bg-gray-900 rounded-lg p-3 font-mono text-xs text-green-400 max-h-48 overflow-auto">
              {logs.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))}
              {isTesting && (
                <div className="flex items-center space-x-2">
                  <div className="w-1 h-3 bg-green-400 animate-pulse"></div>
                  <span>Testing...</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
