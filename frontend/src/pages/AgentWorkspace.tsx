import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listAgents } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelStatusDot } from '../components/ui/molecules/PixelStatusDot'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelButton } from '../components/ui/atoms/PixelButton'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'

const autonomyColors: Record<string, 'green' | 'blue' | 'orange' | 'red'> = {
  L0: 'green',
  L1: 'blue',
  L2: 'orange',
  L3: 'red',
  L4: 'red',
}

export default function AgentWorkspace() {
  const agents = useQuery({ queryKey: ['agents'], queryFn: listAgents })

  if (agents.isLoading) return <PixelSpinner className="p-8" />

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2>AGENT WORKSPACE</h2>
        <Link to="/agents/new">
          <PixelButton>+ NEW AGENT</PixelButton>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(agents.data ?? []).map((agent) => (
          <Link key={agent.agent_id} to={`/agents/${agent.agent_id}`}>
            <PixelCard className="h-full hover:border-[var(--color-primary)] transition-colors cursor-pointer">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="m-0 text-[var(--color-primary)]">{agent.name}</h3>
                  <p className="text-xs text-[var(--color-text-dim)] mt-1">{agent.role}</p>
                </div>
                <PixelStatusDot status={agent.status} />
              </div>
              <p className="text-sm text-[var(--color-text)] line-clamp-2 mb-3">{agent.mission}</p>
              <div className="flex gap-2 flex-wrap">
                <PixelBadge label={agent.autonomy_level} color={autonomyColors[agent.autonomy_level] ?? 'gray'} />
                <PixelBadge label={`${(agent.tools ?? []).length} tools`} color="gray" />
                {(agent.triggers ?? []).length > 0 && (
                  <PixelBadge label="scheduled" color="blue" />
                )}
              </div>
            </PixelCard>
          </Link>
        ))}
      </div>

      {(agents.data ?? []).length === 0 && (
        <p className="text-[var(--color-text-dim)] text-center py-12">
          No agents created yet.{' '}
          <Link to="/agents/new" className="text-[var(--color-primary)]">
            Create your first agent
          </Link>
        </p>
      )}
    </div>
  )
}
