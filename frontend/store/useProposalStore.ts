/**
 * Proposal Store (Zustand)
 * Manages proposal state and actions
 */

import { create } from 'zustand'
import { createClient } from '@/lib/supabase/client'
import type { Database } from '@/types/database'

type ProcessEvent = Database['public']['Tables']['process_events']['Row']

interface ProposalStore {
  // State
  proposals: ProcessEvent[]
  loading: boolean
  error: string | null
  filter: {
    status?: string
    eventType?: string
    search?: string
  }

  // Actions
  fetchProposals: () => Promise<void>
  updateProposal: (id: string, updates: Partial<ProcessEvent>) => Promise<void>
  setFilter: (filter: Partial<ProposalStore['filter']>) => void
  clearError: () => void
}

export const useProposalStore = create<ProposalStore>((set, get) => ({
  // Initial state
  proposals: [],
  loading: false,
  error: null,
  filter: {},

  // Fetch proposals from Supabase
  fetchProposals: async () => {
    set({ loading: true, error: null })
    const supabase = createClient()

    try {
      const { filter } = get()
      let query = supabase
        .from('process_events')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1000)

      // Apply filters
      if (filter.status) {
        query = query.eq('event_metadata->>status', filter.status)
      }
      if (filter.eventType) {
        query = query.eq('event_type', filter.eventType)
      }
      if (filter.search) {
        query = query.or(`event_name.ilike.%${filter.search}%,id.ilike.%${filter.search}%`)
      }

      const { data, error } = await query

      if (error) throw error

      set({ proposals: data || [], loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  // Update a proposal
  updateProposal: async (id: string, updates: Partial<ProcessEvent>) => {
    const supabase = createClient()

    try {
      const { error } = await supabase
        .from('process_events')
        .update(updates)
        .eq('id', id)

      if (error) throw error

      // Update local state
      set((state) => ({
        proposals: state.proposals.map((p) =>
          p.id === id ? { ...p, ...updates } : p
        ),
      }))
    } catch (error: any) {
      set({ error: error.message })
    }
  },

  // Set filter
  setFilter: (filter) => {
    set((state) => ({
      filter: { ...state.filter, ...filter },
    }))
    get().fetchProposals()
  },

  // Clear error
  clearError: () => set({ error: null }),
}))
