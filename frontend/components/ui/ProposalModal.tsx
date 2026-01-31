'use client'

/**
 * Proposal Modal (Logic Card)
 * Displays detailed proposal information with reasoning and RAG context
 */

import { useEffect, useState } from 'react'
import { X, Code, Brain, FileText, CheckCircle, XCircle } from 'lucide-react'
import { useUIStore } from '@/store/useUIStore'
import { useProposalStore } from '@/store/useProposalStore'
import { createClient } from '@/lib/supabase/client'
import type { Database } from '@/types/database'

type ProcessEvent = Database['public']['Tables']['process_events']['Row']

export function ProposalModal() {
  const { modalOpen, selectedProposalId, closeModal } = useUIStore()
  const { proposals } = useProposalStore()
  const [proposal, setProposal] = useState<ProcessEvent | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (selectedProposalId) {
      const found = proposals.find((p) => p.id === selectedProposalId)
      setProposal(found || null)
    }
  }, [selectedProposalId, proposals])

  if (!modalOpen || !proposal) return null

  const metadata = proposal.metadata as any
  const status = proposal.status || 'unknown'

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={closeModal}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Brain className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Proposal Details
              </h2>
              <p className="text-sm text-gray-600">{proposal.id}</p>
            </div>
          </div>
          <button
            onClick={closeModal}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Status Badge */}
          <div className="mb-6">
            <span
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
                status === 'approved'
                  ? 'bg-green-100 text-green-700'
                  : status === 'rejected'
                  ? 'bg-red-100 text-red-700'
                  : status === 'pending'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {status === 'approved' && <CheckCircle className="w-4 h-4" />}
              {status === 'rejected' && <XCircle className="w-4 h-4" />}
              Status: {status}
            </span>
          </div>

          {/* Event Information */}
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Event Information
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Event Name:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {proposal.event_name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Event Type:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {proposal.event_type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Workflow ID:</span>
                  <span className="text-sm font-medium text-gray-900 font-mono text-xs">
                    {proposal.workflow_id || '-'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">User ID:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {proposal.user_id}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Created:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {new Date(proposal.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Metadata */}
            {metadata && Object.keys(metadata).length > 1 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  Metadata
                </h3>
                <div className="bg-gray-900 rounded-lg p-4">
                  <pre className="text-xs text-green-400 font-mono overflow-x-auto">
                    {JSON.stringify(metadata, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* Placeholder for future features */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <h4 className="text-sm font-semibold text-gray-700 mb-1">
                Coming Soon
              </h4>
              <p className="text-sm text-gray-600">
                AI reasoning steps and RAG citations will appear here (Phase 4.3)
              </p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={closeModal}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
