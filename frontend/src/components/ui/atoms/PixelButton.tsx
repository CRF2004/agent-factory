import { type ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'danger' | 'ghost'

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-[var(--color-primary-dim)] text-[var(--color-primary)] border-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-[var(--color-bg)]',
  danger:
    'bg-[color-mix(in_srgb,var(--color-danger)_20%,transparent)] text-[var(--color-danger)] border-[var(--color-danger)] hover:bg-[var(--color-danger)] hover:text-white',
  ghost:
    'bg-transparent text-[var(--color-text-dim)] border-[var(--color-border)] hover:text-[var(--color-text)] hover:border-[var(--color-border-light)]',
}

interface PixelButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: 'sm' | 'md'
}

export function PixelButton({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}: PixelButtonProps) {
  const sizeClass = size === 'sm' ? 'px-3 py-1 text-xs' : 'px-4 py-2 text-sm'
  return (
    <button
      className={`font-[var(--font-heading)] border-2 cursor-pointer transition-colors
        ${sizeClass} ${variantClasses[variant]}
        shadow-[2px_2px_0px_var(--color-border)]
        active:shadow-none active:translate-x-[2px] active:translate-y-[2px]
        disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
