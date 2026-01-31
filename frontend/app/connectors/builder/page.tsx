/**
 * Connector Builder Page
 * No-code custom connector builder with AI assistance
 */

'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { ApiDocAnalyzer, FieldMapper, TestSandbox } from '@/components/builder'
import { ArrowRight, Save, Rocket, Info } from 'lucide-react'

export default function ConnectorBuilderPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [connectorName, setConnectorName] = useState('')
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [mappingsApproved, setMappingsApproved] = useState(false)

  const steps = [
    { id: 1, name: 'API Analysis', description: 'Analyze API documentation' },
    { id: 2, name: 'Field Mapping', description: 'Map fields to unified schema' },
    { id: 3, name: 'Test & Deploy', description: 'Test and deploy connector' }
  ]

  const canProceedToStep2 = analysisComplete && connectorName
  const canProceedToStep3 = mappingsApproved

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Connector Builder</h1>
          <p className="text-gray-600 mt-1">
            Build custom connectors with AI assistance - no coding required
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm text-blue-900 font-medium">AI-Powered Connector Builder</p>
              <p className="text-xs text-blue-700 mt-1">
                Our AI analyzes your API documentation and automatically generates field mappings,
                reducing connector setup time by 70%. Review and approve suggestions before deployment.
              </p>
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    currentStep === step.id
                      ? 'bg-blue-600 text-white'
                      : currentStep > step.id
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step.id}
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${
                      currentStep >= step.id ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </p>
                    <p className="text-xs text-gray-500">{step.description}</p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <ArrowRight className="w-5 h-5 text-gray-400 mx-4" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Connector Name (Always Visible) */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Connector Name
          </label>
          <input
            type="text"
            value={connectorName}
            onChange={(e) => setConnectorName(e.target.value)}
            placeholder="e.g., Shopify, Salesforce, Custom CRM"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="mt-1 text-xs text-gray-500">
            Choose a descriptive name for your custom connector
          </p>
        </div>

        {/* Step 1: API Analysis */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <ApiDocAnalyzer 
              onAnalysisComplete={(endpoints) => {
                console.log('Endpoints:', endpoints)
                setAnalysisComplete(true)
              }}
            />
            
            <div className="flex justify-end">
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!canProceedToStep2}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <span>Continue to Field Mapping</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Field Mapping */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <FieldMapper 
              onMappingsUpdate={(mappings) => {
                const allApproved = mappings.every(m => m.userApproved)
                setMappingsApproved(allApproved)
              }}
            />
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(1)}
                className="flex items-center space-x-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <span>Back</span>
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                disabled={!canProceedToStep3}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <span>Continue to Test</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Test & Deploy */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <TestSandbox 
              connectorName={connectorName}
              onTestComplete={(result) => {
                console.log('Test result:', result)
              }}
            />
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(2)}
                className="flex items-center space-x-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <span>Back</span>
              </button>
              
              <div className="flex items-center space-x-3">
                <button
                  className="flex items-center space-x-2 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Save className="w-5 h-5" />
                  <span>Save Draft</span>
                </button>
                <button
                  className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Rocket className="w-5 h-5" />
                  <span>Deploy Connector</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Need Help?</h3>
          <p className="text-sm text-gray-600 mb-3">
            Check out our documentation for detailed guides on building custom connectors.
          </p>
          <a 
            href="#" 
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View Documentation →
          </a>
        </div>
      </div>
    </AppLayout>
  )
}
