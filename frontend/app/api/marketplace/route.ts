import { createServerSupabaseClient } from '@/lib/supabase/server'

export async function GET() {
  try {
    const supabase = await createServerSupabaseClient()

    // Fetch all marketplace connectors
    const { data: connectors, error } = await supabase
      .from('connector_marketplace')
      .select('*')
      .order('install_count', { ascending: false })

    if (error) {
      console.error('Error fetching marketplace connectors:', error)
      return Response.json({ error: error.message }, { status: 500 })
    }

    return Response.json({ connectors })
  } catch (error) {
    console.error('Marketplace API error:', error)
    return Response.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}
