import { useEffect, type ReactNode } from 'react'
import { PixelButton } from '../atoms/PixelButton'

interface PixelModalProps {
  open: boolean
  title: string
  onClose: () => void
  children: ReactNode
}

export function PixelModal({ open, title, onClose, children }: PixelModalProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div
        className="border-2 border-[var(--color-border)] bg-[var(--color-bg)]
          shadow-[4px_4px_0px_var(--color-border)] w-full max-w-lg mx-4
          animate-slide-down"
      >
        <div className="flex items-center justify-between px-4 py-2 border-b-2 border-[var(--color-border)] bg-[var(--color-panel)]">
          <h3 className="text-[var(--color-primary)] m-0">{title}</h3>
          <PixelButton variant="ghost" size="sm" onClick={onClose}>
            X
          </PixelButton>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  )
}
