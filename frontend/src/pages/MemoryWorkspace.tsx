import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { listMemoryItems, type MemoryItem } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelStatusDot } from '../components/ui/molecules/PixelStatusDot'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelButton } from '../components/ui/atoms/PixelButton'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'

const typeColors: Record<string, 'blue' | 'orange' | 'green'> = {
  knowledge: 'blue',
  experience: 'orange',
  skill: 'green',
}

const statusColors: Record<string, 'green' | 'orange' | 'red' | 'gray'> = {
  candidate: 'orange',
  approved: 'green',
  active: 'green',
  deprecated: 'gray',
  rejected: 'red',
  conflict: 'red',
}

export default function MemoryWorkspace() {
  const memories = useQuery({ queryKey: ['memories'], queryFn: listMemoryItems, refetchInterval: 10000 })
  const [filter, setFilter] = useState<string>('all')

  if (memories.isLoading) return <PixelSpinner className="p-8" />

  const data = memories.data ?? []
  const filtered = filter === 'all' ? data : data.filter((m) => m.status === filter)
  const candidateCount = data.filter((m) => m.status === 'candidate').length

  return (
    <div>
      <h2 className="mb-6">MEMORY WORKSPACE</h2>

      <div className="flex gap-2 mb-4 flex-wrap">
        {['all', 'candidate', 'active', 'approved', 'rejected'].map((f) => (
          <PixelButton
            key={f}
            variant={filter === f ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setFilter(f)}
          >
            {f.toUpperCase()}
            {f === 'candidate' && candidateCount > 0 ? ` (${candidateCount})` : ''}
          </PixelButton>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-3">
        {filtered.map((m: MemoryItem) => (
          <PixelCard key={m.id}>
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="text-[var(--color-primary)] m-0">{m.title}</h4>
                <p className="text-xs text-[var(--color-text-dim)] mt-1">
                  {(m.summary ?? m.content).slice(0, 120)}
                </p>
              </div>
              <div className="flex gap-2 flex-shrink-0 ml-4">
                <PixelBadge label={m.type} color={typeColors[m.type] ?? 'gray'} />
                <PixelBadge label={m.status} color={statusColors[m.status] ?? 'gray'} />
              </div>
            </div>
            <div className="flex items-center gap-3 text-[10px] text-[var(--color-text-dim)]">
              <span>
                <PixelStatusDot status={m.status} />
              </span>
              <span>Confidence: {(m.confidence * 100).toFixed(0)}%</span>
              {m.reliability_score != null && (
                <span>Reliability: {((m.reliability_score ?? 0) * 100).toFixed(0)}%</span>
              )}
              {m.source && <span>Source: {m.source}</span>}
              {m.tags.length > 0 && (
                <span className="flex gap-1">
                  {m.tags.map((tag: string) => (
                    <span key={tag} className="border border-[var(--color-border)] px-1">
                      {tag}
                    </span>
                  ))}
                </span>
              )}
              {m.related_projects.length > 0 && (
                <span>Projects: {m.related_projects.join(', ')}</span>
              )}
            </div>
          </PixelCard>
        ))}

        {filtered.length === 0 && (
          <p className="text-sm text-[var(--color-text-dim)] text-center py-8">
            No memory items found.
          </p>
        )}
      </div>
    </div>
  )
}
