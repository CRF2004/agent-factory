const statusColors: Record<string, string> = {
  active: 'bg-[var(--color-primary)]',
  idle: 'bg-[var(--color-text-dim)]',
  running: 'bg-[var(--color-accent)]',
  completed: 'bg-[var(--color-primary)]',
  failed: 'bg-[var(--color-danger)]',
  cancelled: 'bg-[var(--color-warning)]',
  pending: 'bg-[var(--color-warning)]',
  disabled: 'bg-[var(--color-border)]',
  error: 'bg-[var(--color-danger)]',
  blocked: 'bg-[var(--color-warning)]',
  waiting_approval: 'bg-[var(--color-warning)]',
  candidate: 'bg-[var(--color-text-dim)]',
  approved: 'bg-[var(--color-primary)]',
  rejected: 'bg-[var(--color-danger)]',
}

export function PixelStatusDot({
  status,
  label,
}: {
  status: string
  label?: string
}) {
  const dotColor = statusColors[status] || 'bg-[var(--color-border)]'
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={`inline-block w-2.5 h-2.5 ${dotColor}`}
        style={{
          animation:
            status === 'running' ? 'fade-in 0.5s ease-in-out infinite alternate' : 'none',
        }}
      />
      {label && <span className="text-sm text-[var(--color-text-dim)]">{label}</span>}
    </span>
  )
}
