/**
 * Analytics API Route
 * Fetch real-time analytics metrics
 */

import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
  try {
    const supabase = await createServerSupabaseClient()
    const { searchParams } = new URL(request.url)
    const timeRange = searchParams.get('timeRange') || '7d'

    // Get user session
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Calculate date range
    const now = new Date()
    const daysAgo = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90
    const startDate = new Date(now)
    startDate.setDate(startDate.getDate() - daysAgo)

    // Fetch connector health (mock data for now)
    const connectorHealth = {
      healthy: 25,
      degraded: 2,
      failed: 1
    }

    // Fetch sync metrics (mock data for now)
    const syncMetrics = {
      last24h: 12456,
      last7d: 87234,
      last30d: 345678,
      successRate: 98.5,
      trend: 'up' as const,
      trendPercentage: 5.2
    }

    // Fetch performance metrics (mock data for now)
    const performanceMetrics = {
      avgResponseTime: 234,
      p95ResponseTime: 567,
      errorRate: 1.5,
      successRate: 98.5
    }

    // Return combined metrics
    return NextResponse.json({
      connectorHealth,
      syncMetrics,
      performanceMetrics,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Analytics API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
