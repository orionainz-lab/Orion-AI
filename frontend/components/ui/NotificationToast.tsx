'use client'

/**
 * Notification Toast Component
 * Displays toast notifications from the UI store
 */

import { useEffect } from 'react'
import { useUIStore } from '@/store/useUIStore'
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react'
import { cn } from '@/lib/utils'

export function NotificationToast() {
  const { notifications, removeNotification } = useUIStore()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {notifications.map((notification) => {
        const icons = {
          success: CheckCircle,
          error: XCircle,
          info: Info,
          warning: AlertTriangle,
        }

        const colors = {
          success: 'bg-green-50 text-green-900 border-green-200',
          error: 'bg-red-50 text-red-900 border-red-200',
          info: 'bg-blue-50 text-blue-900 border-blue-200',
          warning: 'bg-yellow-50 text-yellow-900 border-yellow-200',
        }

        const iconColors = {
          success: 'text-green-600',
          error: 'text-red-600',
          info: 'text-blue-600',
          warning: 'text-yellow-600',
        }

        const Icon = icons[notification.type]

        return (
          <div
            key={notification.id}
            className={cn(
              'flex items-start gap-3 p-4 rounded-lg border shadow-lg animate-in slide-in-from-right',
              colors[notification.type]
            )}
          >
            <Icon className={cn('w-5 h-5 flex-shrink-0', iconColors[notification.type])} />
            <p className="text-sm font-medium flex-1">{notification.message}</p>
            <button
              onClick={() => removeNotification(notification.id)}
              className="flex-shrink-0 hover:opacity-70 transition-opacity"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
