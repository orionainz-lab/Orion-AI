/**
 * Field Mapper Component
 * Map API fields to unified schema with AI suggestions
 */

'use client'

import { useState } from 'react'
import { ArrowRight, Sparkles, Check, X } from 'lucide-react'

interface FieldMapping {
  sourceField: string
  targetField: string
  confidence: number
  transformation?: string
  reasoning: string
  userApproved: boolean
}

interface FieldMapperProps {
  suggestedMappings?: FieldMapping[]
  onMappingsUpdate?: (mappings: FieldMapping[]) => void
}

const defaultMappings: FieldMapping[] = [
  {
    sourceField: 'email',
    targetField: 'customer_email',
    confidence: 0.95,
    reasoning: 'Direct email field match',
    userApproved: false
  },
  {
    sourceField: 'name',
    targetField: 'customer_name',
    confidence: 0.90,
    reasoning: 'Name field matches unified schema',
    userApproved: false
  },
  {
    sourceField: 'contact.phone',
    targetField: 'customer_phone',
    confidence: 0.85,
    transformation: 'format_phone',
    reasoning: 'Nested phone field, requires E.164 formatting',
    userApproved: false
  },
  {
    sourceField: 'company_name',
    targetField: 'company',
    confidence: 0.88,
    reasoning: 'Company name field mapping',
    userApproved: false
  }
]

export function FieldMapper({ suggestedMappings = defaultMappings, onMappingsUpdate }: FieldMapperProps) {
  const [mappings, setMappings] = useState<FieldMapping[]>(suggestedMappings)

  const handleApprove = (index: number) => {
    const updated = [...mappings]
    updated[index].userApproved = true
    setMappings(updated)
    onMappingsUpdate?.(updated)
  }

  const handleReject = (index: number) => {
    const updated = mappings.filter((_, i) => i !== index)
    setMappings(updated)
    onMappingsUpdate?.(updated)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-50'
    if (confidence >= 0.8) return 'text-yellow-600 bg-yellow-50'
    return 'text-orange-600 bg-orange-50'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Sparkles className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">AI Field Mapping</h3>
      </div>

      <p className="text-sm text-gray-600 mb-6">
        Review and approve AI-suggested field mappings. You can edit or reject any suggestion.
      </p>

      <div className="space-y-4">
        {mappings.map((mapping, index) => (
          <div 
            key={index}
            className={`p-4 rounded-lg border-2 transition-all ${
              mapping.userApproved 
                ? 'border-green-200 bg-green-50' 
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              {/* Source → Target */}
              <div className="flex items-center space-x-3 flex-1">
                <code className="px-2 py-1 bg-white rounded text-sm font-mono text-blue-600 border border-blue-200">
                  {mapping.sourceField}
                </code>
                <ArrowRight className="w-4 h-4 text-gray-400" />
                <code className="px-2 py-1 bg-white rounded text-sm font-mono text-purple-600 border border-purple-200">
                  {mapping.targetField}
                </code>
              </div>

              {/* Confidence Badge */}
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${getConfidenceColor(mapping.confidence)}`}>
                {(mapping.confidence * 100).toFixed(0)}% confident
              </span>
            </div>

            {/* Transformation */}
            {mapping.transformation && (
              <div className="mb-2 text-xs text-gray-600">
                <span className="font-medium">Transformation:</span>{' '}
                <code className="px-1.5 py-0.5 bg-white rounded text-purple-600 border border-gray-200">
                  {mapping.transformation}()
                </code>
              </div>
            )}

            {/* Reasoning */}
            <p className="text-sm text-gray-600 mb-3 italic">
              {mapping.reasoning}
            </p>

            {/* Actions */}
            {!mapping.userApproved && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleApprove(index)}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  <span>Approve</span>
                </button>
                <button
                  onClick={() => handleReject(index)}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition-colors"
                >
                  <X className="w-4 h-4" />
                  <span>Reject</span>
                </button>
              </div>
            )}

            {mapping.userApproved && (
              <div className="flex items-center space-x-2 text-green-600 text-sm">
                <Check className="w-4 h-4" />
                <span className="font-medium">Approved</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            {mappings.filter(m => m.userApproved).length} of {mappings.length} mappings approved
          </span>
          {mappings.every(m => m.userApproved) && (
            <span className="text-green-600 font-medium flex items-center space-x-1">
              <Check className="w-4 h-4" />
              <span>All mappings approved</span>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
