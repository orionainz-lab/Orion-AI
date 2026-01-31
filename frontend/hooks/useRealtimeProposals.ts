/**
 * Realtime Proposals Hook
 * Subscribes to proposal changes via Supabase Realtime
 */

import { useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useProposalStore } from '@/store/useProposalStore'
import { useUIStore } from '@/store/useUIStore'
import type { Database } from '@/types/database'

type ProcessEvent = Database['public']['Tables']['process_events']['Row']

export function useRealtimeProposals() {
  const { proposals, fetchProposals } = useProposalStore()
  const { addNotification } = useUIStore()

  useEffect(() => {
    const supabase = createClient()

    // Create channel for process_events table
    const channel = supabase
      .channel('process_events_changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'process_events',
        },
        (payload) => {
          console.log('New proposal:', payload.new)
          const newProposal = payload.new as ProcessEvent

          // Add to store
          useProposalStore.setState((state) => ({
            proposals: [newProposal, ...state.proposals],
          }))

          // Show notification
          addNotification({
            type: 'info',
            message: `New proposal: ${newProposal.event_name}`,
            duration: 5000,
          })
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'process_events',
        },
        (payload) => {
          console.log('Proposal updated:', payload.new)
          const updatedProposal = payload.new as ProcessEvent

          // Update in store
          useProposalStore.setState((state) => ({
            proposals: state.proposals.map((p) =>
              p.id === updatedProposal.id ? updatedProposal : p
            ),
          }))

          // Show notification for status changes
          const oldStatus = (payload.old as ProcessEvent).status
          const newStatus = updatedProposal.status
          if (oldStatus !== newStatus) {
            addNotification({
              type: 'success',
              message: `Proposal ${updatedProposal.id} status changed to ${newStatus}`,
              duration: 3000,
            })
          }
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'DELETE',
          schema: 'public',
          table: 'process_events',
        },
        (payload) => {
          console.log('Proposal deleted:', payload.old)
          const deletedProposal = payload.old as ProcessEvent

          // Remove from store
          useProposalStore.setState((state) => ({
            proposals: state.proposals.filter((p) => p.id !== deletedProposal.id),
          }))
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log('Realtime connected')
        } else if (status === 'CHANNEL_ERROR') {
          console.error('Realtime connection error')
          addNotification({
            type: 'error',
            message: 'Real-time connection lost. Reconnecting...',
            duration: 5000,
          })
        } else if (status === 'TIMED_OUT') {
          console.error('Realtime connection timed out')
        }
      })

    // Cleanup on unmount
    return () => {
      supabase.removeChannel(channel)
    }
  }, [addNotification])

  // Initial fetch
  useEffect(() => {
    fetchProposals()
  }, [fetchProposals])

  return { proposals }
}
