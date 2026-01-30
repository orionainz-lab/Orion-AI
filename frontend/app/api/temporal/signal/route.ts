/**
 * Temporal Signal API Route
 * Sends signals to Temporal workflows
 */

import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'
import { z } from 'zod'

// Validation schema
const SignalRequestSchema = z.object({
  workflowId: z.string().min(1, 'Workflow ID is required'),
  signalName: z.string().min(1, 'Signal name is required'),
  signalArgs: z.record(z.any()).optional().default({}),
})

export async function POST(request: NextRequest) {
  try {
    // 1. Validate user session
    const supabase = await createServerSupabaseClient()
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized', message: 'Please sign in to continue' },
        { status: 401 }
      )
    }

    // 2. Parse and validate request body
    const body = await request.json()
    const validationResult = SignalRequestSchema.safeParse(body)

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: 'Invalid request',
          details: validationResult.error.errors,
        },
        { status: 400 }
      )
    }

    const { workflowId, signalName, signalArgs } = validationResult.data

    // 3. Connect to Temporal
    // Note: @temporalio/client is server-side only
    try {
      const { Connection, WorkflowClient } = await import('@temporalio/client')

      const connection = await Connection.connect({
        address: process.env.TEMPORAL_ADDRESS || 'localhost:7233',
      })

      const client = new WorkflowClient({ connection })

      // 4. Get workflow handle
      const handle = client.getHandle(workflowId)

      // 5. Send signal
      await handle.signal(signalName, signalArgs)

      // Log success
      console.log('Signal sent successfully:', {
        workflowId,
        signalName,
        user: session.user.email,
      })

      return NextResponse.json({
        success: true,
        message: 'Signal sent successfully',
        workflowId,
        signalName,
      })
    } catch (temporalError: any) {
      console.error('Temporal error:', temporalError)

      // Handle specific Temporal errors
      if (temporalError.message?.includes('workflow not found')) {
        return NextResponse.json(
          {
            error: 'Workflow not found',
            message: `Workflow ${workflowId} does not exist`,
          },
          { status: 404 }
        )
      }

      return NextResponse.json(
        {
          error: 'Temporal error',
          message: temporalError.message || 'Failed to send signal',
        },
        { status: 500 }
      )
    }
  } catch (error: any) {
    console.error('Signal API error:', error)

    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error.message || 'An unexpected error occurred',
      },
      { status: 500 }
    )
  }
}
