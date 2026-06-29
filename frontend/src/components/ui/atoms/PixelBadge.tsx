type BadgeColor = 'green' | 'orange' | 'red' | 'blue' | 'gray'

const colorMap: Record<BadgeColor, string> = {
  green: 'text-[var(--color-primary)] border-[var(--color-primary)] bg-[color-mix(in_srgb,var(--color-primary)_15%,transparent)]',
  orange: 'text-[var(--color-warning)] border-[var(--color-warning)] bg-[color-mix(in_srgb,var(--color-warning)_15%,transparent)]',
  red: 'text-[var(--color-danger)] border-[var(--color-danger)] bg-[color-mix(in_srgb,var(--color-danger)_15%,transparent)]',
  blue: 'text-[var(--color-accent)] border-[var(--color-accent)] bg-[color-mix(in_srgb,var(--color-accent)_15%,transparent)]',
  gray: 'text-[var(--color-text-dim)] border-[var(--color-border)] bg-[var(--color-panel)]',
}

interface PixelBadgeProps {
  label: string
  color?: BadgeColor
}

export function PixelBadge({ label, color = 'gray' }: PixelBadgeProps) {
  return (
    <span
      className={`inline-block px-2 py-0.5 text-[10px] font-[var(--font-heading)] border
        ${colorMap[color]}`}
    >
      {label}
    </span>
  )
}
