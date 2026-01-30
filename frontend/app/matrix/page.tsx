/**
 * Matrix Grid Page
 * Displays all proposals in AG Grid with real-time updates
 */

'use client'

import { AppLayout } from '@/components/layout/AppLayout'
import { MatrixGridV2 } from '@/components/grid/MatrixGridV2'

export default function MatrixPage() {
  return (
    <AppLayout>
      <div className="h-full">
        <MatrixGridV2 />
      </div>
    </AppLayout>
  )
}
