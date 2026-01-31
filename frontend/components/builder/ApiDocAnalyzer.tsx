/**
 * API Documentation Analyzer
 * Upload and analyze API documentation for schema mapping
 */

'use client'

import { useState } from 'react'
import { Upload, FileText, Loader2, CheckCircle2 } from 'lucide-react'

interface ApiDocAnalyzerProps {
  onAnalysisComplete?: (endpoints: Array<{path: string; method: string; description: string}>) => void
}

export function ApiDocAnalyzer({ onAnalysisComplete }: ApiDocAnalyzerProps) {
  const [apiDocsUrl, setApiDocsUrl] = useState('')
  const [sampleResponse, setSampleResponse] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)

  const handleAnalyze = async () => {
    if (!apiDocsUrl && !sampleResponse) return

    setIsAnalyzing(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsAnalyzing(false)
      setAnalysisComplete(true)
      onAnalysisComplete?.([
        { path: '/customers', method: 'GET', description: 'List customers' },
        { path: '/customers', method: 'POST', description: 'Create customer' }
      ])
    }, 2000)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <FileText className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">API Documentation</h3>
      </div>

      <div className="space-y-4">
        {/* API Docs URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Documentation URL (Optional)
          </label>
          <input
            type="url"
            value={apiDocsUrl}
            onChange={(e) => setApiDocsUrl(e.target.value)}
            placeholder="https://api.example.com/docs"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isAnalyzing || analysisComplete}
          />
          <p className="mt-1 text-xs text-gray-500">
            Provide OpenAPI spec or documentation URL for automatic analysis
          </p>
        </div>

        {/* Sample Response */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sample API Response (Required)
          </label>
          <textarea
            value={sampleResponse}
            onChange={(e) => setSampleResponse(e.target.value)}
            placeholder='{"id": "cust_123", "email": "user@example.com", "name": "John Doe"}'
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            disabled={isAnalyzing || analysisComplete}
          />
          <p className="mt-1 text-xs text-gray-500">
            Paste a sample JSON response from the API
          </p>
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={!sampleResponse || isAnalyzing || analysisComplete}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing with AI...</span>
            </>
          ) : analysisComplete ? (
            <>
              <CheckCircle2 className="w-5 h-5" />
              <span>Analysis Complete</span>
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              <span>Analyze API</span>
            </>
          )}
        </button>

        {/* Analysis Result */}
        {analysisComplete && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-green-900">Analysis Complete</p>
                <p className="text-xs text-green-700 mt-1">
                  Found 2 endpoints and identified 5 fields for mapping
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
