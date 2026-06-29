import { NavLink } from 'react-router-dom'
import type { ReactNode } from 'react'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/agents', label: 'Agents' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/memory', label: 'Memory' },
  { to: '/approvals', label: 'Approvals' },
]

const linkClasses = ({ isActive }: { isActive: boolean }) =>
  `block px-4 py-3 text-xs font-[var(--font-heading)] border-b-2 transition-colors ${
    isActive
      ? 'text-[var(--color-primary)] border-[var(--color-primary)] bg-[var(--color-panel)]'
      : 'text-[var(--color-text-dim)] border-transparent hover:text-[var(--color-text)] hover:border-[var(--color-border)]'
  }`

export function PixelLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-52 flex-shrink-0 border-r-2 border-[var(--color-border)] bg-[var(--color-bg)] flex flex-col">
        <div className="px-4 py-4 border-b-2 border-[var(--color-border)]">
          <h1 className="text-sm text-[var(--color-primary)] leading-tight">
            AGENT
            <br />
            FACTORY
          </h1>
          <p className="text-[10px] text-[var(--color-text-dim)] mt-1">
            v0.1.0
          </p>
        </div>
        <nav className="flex-1 py-2">
          {navItems.map(({ to, label }) => (
            <NavLink key={to} to={to} end={to === '/'} className={linkClasses}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-3 border-t-2 border-[var(--color-border)] text-[10px] text-[var(--color-text-dim)]">
          <NavLink
            to="/agents/new"
            className={({ isActive }) =>
              `block px-3 py-2 text-center border-2 font-[var(--font-heading)] ${
                isActive
                  ? 'text-[var(--color-primary)] border-[var(--color-primary)] bg-[var(--color-panel)]'
                  : 'text-[var(--color-text)] border-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-[var(--color-bg)]'
              }`
            }
          >
            + NEW AGENT
          </NavLink>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  )
}
