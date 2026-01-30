/**
 * UI Store (Zustand)
 * Manages UI state (modals, sidebar, notifications)
 */

import { create } from 'zustand'

interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

interface UIStore {
  // State
  sidebarOpen: boolean
  modalOpen: boolean
  selectedProposalId: string | null
  notifications: Notification[]

  // Actions
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  openModal: (proposalId: string) => void
  closeModal: () => void
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
}

export const useUIStore = create<UIStore>((set, get) => ({
  // Initial state
  sidebarOpen: false,
  modalOpen: false,
  selectedProposalId: null,
  notifications: [],

  // Toggle sidebar
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  // Set sidebar state
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Open proposal modal
  openModal: (proposalId) => set({ modalOpen: true, selectedProposalId: proposalId }),

  // Close modal
  closeModal: () => set({ modalOpen: false, selectedProposalId: null }),

  // Add notification
  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newNotification = { ...notification, id }

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }))

    // Auto-remove after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        get().removeNotification(id)
      }, notification.duration || 5000)
    }
  },

  // Remove notification
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}))
