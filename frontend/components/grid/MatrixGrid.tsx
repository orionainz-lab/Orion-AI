'use client'

/**
 * Matrix Grid Component
 * AG Grid implementation for displaying proposals
 */

import { useCallback, useMemo, useRef, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import type { ColDef } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

interface Proposal {
  id: string
  workflow_id: string
  status: 'pending' | 'approved' | 'rejected' | 'processing'
  event_name: string
  user_id: string
  created_at: string
}

// Status badge renderer
function StatusCellRenderer(props: { value: string }) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
    processing: 'bg-blue-100 text-blue-700',
  }

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-medium ${
        colors[props.value as keyof typeof colors] || 'bg-gray-100 text-gray-700'
      }`}
    >
      {props.value}
    </span>
  )
}

// Timestamp renderer
function TimestampCellRenderer(props: { value: string }) {
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

export function MatrixGrid() {
  const gridRef = useRef<AgGridReact>(null)
  const [rowData] = useState<Proposal[]>(() => {
    // Generate mock data
    const statuses: Proposal['status'][] = ['pending', 'approved', 'rejected', 'processing']
    const events = ['code_generated', 'approval_requested', 'workflow_started', 'task_completed']
    const users = ['user-001', 'user-002', 'user-003', 'user-004', 'user-005']

    return Array.from({ length: 1000 }, (_, i) => ({
      id: `prop-${i.toString().padStart(6, '0')}`,
      workflow_id: `wf-${Math.random().toString(36).substr(2, 9)}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      event_name: events[Math.floor(Math.random() * events.length)],
      user_id: users[Math.floor(Math.random() * users.length)],
      created_at: new Date(
        Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000
      ).toISOString(),
    }))
  })

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
        field: 'status',
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
  }, [])

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            All Proposals
          </h2>
          <p className="text-sm text-gray-600">
            {rowData.length.toLocaleString()} total proposals
          </p>
        </div>
        <button
          onClick={onExportCSV}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Export CSV
        </button>
      </div>

      {/* Grid */}
      <div className="ag-theme-alpine flex-1" style={{ height: 600 }}>
        <AgGridReact
          ref={gridRef}
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          animateRows={false}
          rowBuffer={10}
        />
      </div>
    </div>
  )
}
