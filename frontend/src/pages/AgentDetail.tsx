import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { getAgent, listTasks } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelStatusDot } from '../components/ui/molecules/PixelStatusDot'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'

export default function AgentDetail() {
  const { id } = useParams<{ id: string }>()
  const agent = useQuery({
    queryKey: ['agent', id],
    queryFn: () => getAgent(id!),
    enabled: !!id,
  })
  const tasks = useQuery({
    queryKey: ['tasks'],
    queryFn: listTasks,
  })

  if (agent.isLoading) return <PixelSpinner className="p-8" />
  if (agent.isError) return <p className="text-[var(--color-danger)]">Failed to load agent</p>

  const a = agent.data!
  const agentTasks = (tasks.data ?? []).filter((t) => t.owner_agent === id)
  const recentRuns = agentTasks.slice(0, 10)

  return (
    <div>
      <h2 className="mb-6">
        {a.name}
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <PixelCard title="STATUS">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-[var(--color-text-dim)]">Status</span>
              <span className="flex items-center gap-1">
                <PixelStatusDot status={a.status} label={a.status} />
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[var(--color-text-dim)]">Role</span>
              <span>{a.role}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[var(--color-text-dim)]">Autonomy</span>
              <PixelBadge label={a.autonomy_level} color="orange" />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[var(--color-text-dim)]">Task Count</span>
              <span>{agentTasks.length}</span>
            </div>
          </div>
        </PixelCard>

        <PixelCard title="MISSION">
          <p className="text-sm text-[var(--color-text)]">{a.mission}</p>
        </PixelCard>

        <PixelCard title="TOOLS">
          <div className="flex flex-wrap gap-2">
            {(a.tools ?? []).map((t: Record<string, unknown>) => (
              <PixelBadge
                key={t.tool_id as string}
                label={`${t.tool_id} (${t.permission})`}
                color="blue"
              />
            ))}
            {(a.tools ?? []).length === 0 && (
              <span className="text-sm text-[var(--color-text-dim)]">No tools configured</span>
            )}
          </div>
        </PixelCard>

        <PixelCard title="ACTIONS">
          <div className="space-y-1">
            <p className="text-xs text-[var(--color-text-dim)]">
              Auto:{' '}
              <span className="text-[var(--color-primary)]">
                {(a.actions as Record<string, unknown>)?.auto ? ((a.actions as Record<string, unknown>).auto as string[]).join(', ') : 'none'}
              </span>
            </p>
            <p className="text-xs text-[var(--color-text-dim)]">
              Approval Required:{' '}
              <span className="text-[var(--color-warning)]">
                {(a.actions as Record<string, unknown>)?.approval_required ? ((a.actions as Record<string, unknown>).approval_required as string[]).join(', ') : 'none'}
              </span>
            </p>
          </div>
        </PixelCard>
      </div>

      <PixelCard title="RECENT TASKS">
        {recentRuns.length === 0 ? (
          <p className="text-sm text-[var(--color-text-dim)]">No tasks yet</p>
        ) : (
          <div className="space-y-1">
            {recentRuns.map((t) => (
              <Link
                key={t.task_id}
                to="/tasks"
                className="flex items-center justify-between p-2 border border-[var(--color-border)] hover:bg-[var(--color-panel)]"
              >
                <div className="flex items-center gap-2">
                  <PixelStatusDot status={t.status} />
                  <span className="text-sm">{t.title}</span>
                </div>
                <PixelBadge label={t.status} color={t.status === 'completed' ? 'green' : 'gray'} />
              </Link>
            ))}
          </div>
        )}
      </PixelCard>
    </div>
  )
}
