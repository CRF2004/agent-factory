import type { ReactNode } from 'react'

interface PixelCardProps {
  title?: string
  children: ReactNode
  className?: string
}

export function PixelCard({ title, children, className = '' }: PixelCardProps) {
  return (
    <div
      className={`border-2 border-[var(--color-border)] bg-[var(--color-panel)]
        shadow-[3px_3px_0px_var(--color-border)] ${className}`}
    >
      {title && (
        <div className="px-4 py-2 border-b-2 border-[var(--color-border)] bg-[var(--color-panel-light)]">
          <h3 className="text-[var(--color-primary)] m-0">{title}</h3>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  )
}
