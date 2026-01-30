'use client'

/**
 * Matrix Grid V2 - With Real Data & Actions
 * AG Grid with Supabase integration and Temporal signals
 */

import { useCallback, useMemo, useRef, useEffect } from 'react'
import { AgGridReact } from 'ag-grid-react'
import type { ColDef } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useProposalStore } from '@/store/useProposalStore'
import { useUIStore } from '@/store/useUIStore'
import { useRealtimeProposals } from '@/hooks/useRealtimeProposals'
import type { Database } from '@/types/database'

type ProcessEvent = Database['public']['Tables']['process_events']['Row']

// Status badge renderer
function StatusCellRenderer(props: { value: any; data: ProcessEvent }) {
  const status = props.data.event_metadata?.status || 'unknown'
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
    processing: 'bg-blue-100 text-blue-700',
    unknown: 'bg-gray-100 text-gray-700',
  }

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-medium ${colors[status]}`}
    >
      {status}
    </span>
  )
}

// Timestamp renderer
function TimestampCellRenderer(props: { value: string }) {
  if (!props.value) return <span className="text-sm text-gray-400">-</span>

  const date = new Date(props.value)
  return (
    <span className="text-sm text-gray-600">
      {date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })}
    </span>
  )
}

// Actions cell renderer
function ActionsCellRenderer(props: { data: ProcessEvent }) {
  const { addNotification } = useUIStore()
  const { updateProposal } = useProposalStore()
  const [loading, setLoading] = React.useState(false)

  const handleAction = async (action: 'approve' | 'reject') => {
    setLoading(true)

    try {
      // Send signal to Temporal workflow
      const response = await fetch('/api/temporal/signal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflowId: props.data.workflow_id || `workflow-${props.data.id}`,
          signalName: action === 'approve' ? 'approve_signal' : 'reject_signal',
          signalArgs: {
            proposalId: props.data.id,
            userId: 'current-user',
            action,
            timestamp: new Date().toISOString(),
          },
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Failed to send signal')
      }

      // Update local state
      await updateProposal(props.data.id, {
        event_metadata: {
          ...props.data.event_metadata,
          status: action === 'approve' ? 'approved' : 'rejected',
        },
      })

      addNotification({
        type: 'success',
        message: `Proposal ${action === 'approve' ? 'approved' : 'rejected'} successfully`,
        duration: 3000,
      })
    } catch (error: any) {
      console.error('Action error:', error)
      addNotification({
        type: 'error',
        message: error.message || 'Failed to process action',
        duration: 5000,
      })
    } finally {
      setLoading(false)
    }
  }

  const status = props.data.event_metadata?.status
  const isPending = status === 'pending' || !status

  if (!isPending) {
    return <span className="text-sm text-gray-400">-</span>
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => handleAction('approve')}
        disabled={loading}
        className="p-1.5 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50"
        title="Approve"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
        ) : (
          <CheckCircle className="w-4 h-4 text-green-600" />
        )}
      </button>
      <button
        onClick={() => handleAction('reject')}
        disabled={loading}
        className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
        title="Reject"
      >
        <XCircle className="w-4 h-4 text-red-600" />
      </button>
    </div>
  )
}

// Import React for useState in cell renderer
import React from 'react'

export function MatrixGridV2() {
  const gridRef = useRef<AgGridReact>(null)
  const { proposals, loading, error } = useProposalStore()
  const { addNotification, openModal } = useUIStore()

  // Subscribe to realtime updates
  useRealtimeProposals()

  // Handle row click to open modal
  const onRowClicked = useCallback(
    (event: any) => {
      if (event.data) {
        openModal(event.data.id)
      }
    },
    [openModal]
  )

  const columnDefs = useMemo<ColDef[]>(
    () => [
      { field: 'id', headerName: 'ID', width: 150, sortable: true },
      {
        field: 'workflow_id',
        headerName: 'Workflow',
        width: 180,
        sortable: true,
      },
      {
        field: 'event_metadata',
        headerName: 'Status',
        width: 130,
        cellRenderer: StatusCellRenderer,
        filter: 'agSetColumnFilter',
        sortable: true,
      },
      {
        field: 'event_name',
        headerName: 'Event',
        width: 200,
        sortable: true,
        filter: true,
      },
      {
        field: 'user_id',
        headerName: 'User',
        width: 130,
        sortable: true,
        filter: true,
      },
      {
        field: 'created_at',
        headerName: 'Created',
        width: 180,
        cellRenderer: TimestampCellRenderer,
        sortable: true,
        sort: 'desc',
      },
      {
        field: 'id',
        headerName: 'Actions',
        width: 120,
        cellRenderer: ActionsCellRenderer,
        sortable: false,
        filter: false,
      },
    ],
    []
  )

  const defaultColDef = useMemo<ColDef>(
    () => ({
      sortable: true,
      filter: false,
      resizable: true,
    }),
    []
  )

  const onExportCSV = useCallback(() => {
    gridRef.current?.api.exportDataAsCsv({
      fileName: `proposals-${new Date().toISOString()}.csv`,
    })
    addNotification({
      type: 'success',
      message: 'CSV exported successfully',
      duration: 3000,
    })
  }, [addNotification])

  // Show error notification
  useEffect(() => {
    if (error) {
      addNotification({
        type: 'error',
        message: error,
        duration: 5000,
      })
    }
  }, [error, addNotification])

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            All Proposals
          </h2>
          <p className="text-sm text-gray-600">
            {loading
              ? 'Loading...'
              : `${proposals.length.toLocaleString()} total proposals`}
          </p>
        </div>
        <button
          onClick={onExportCSV}
          disabled={loading || proposals.length === 0}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Export CSV
        </button>
      </div>

      {/* Grid */}
      <div className="ag-theme-alpine flex-1" style={{ height: 600 }}>
        <AgGridReact
          ref={gridRef}
          rowData={proposals}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          animateRows={false}
          rowBuffer={10}
          loading={loading}
          onRowClicked={onRowClicked}
          rowClass="cursor-pointer"
        />
      </div>
    </div>
  )
}
