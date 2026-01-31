/**
 * Marketplace Data Hook
 * Fetch connectors from marketplace
 */

'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { ConnectorMarketplace } from '@/types/database'

export function useMarketplace() {
  const [connectors, setConnectors] = useState<ConnectorMarketplace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchConnectors = async () => {
      try {
        setLoading(true)
        const supabase = createClient()

        const { data, error: fetchError } = await supabase
          .from('connector_marketplace')
          .select('*')
          .order('install_count', { ascending: false })

        if (fetchError) throw fetchError
        setConnectors(data || [])
      } catch (err) {
        console.error('Error fetching marketplace:', err)
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchConnectors()
  }, [])

  return { connectors, loading, error, refetch: () => setLoading(true) }
}
