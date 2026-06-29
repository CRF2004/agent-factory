export function PixelSpinner({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="inline-block w-2 h-2 bg-[var(--color-primary)]"
          style={{
            animation: `fade-in 0.6s ease-in-out ${i * 0.15}s infinite alternate`,
          }}
        />
      ))}
    </div>
  )
}
