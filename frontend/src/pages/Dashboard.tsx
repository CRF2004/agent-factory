import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listAgents, listTasks, listApprovals, listMemoryItems } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelStatusDot } from '../components/ui/molecules/PixelStatusDot'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'

export default function Dashboard() {
  const agents = useQuery({ queryKey: ['agents'], queryFn: listAgents })
  const tasks = useQuery({ queryKey: ['tasks'], queryFn: listTasks })
  const approvals = useQuery({ queryKey: ['approvals'], queryFn: listApprovals })
  const memories = useQuery({ queryKey: ['memories'], queryFn: listMemoryItems })

  const pendingApprovals = approvals.data?.filter((a) => a.status === 'pending') ?? []
  const runningTasks = tasks.data?.filter((t) => t.status === 'running') ?? []
  const failedTasks = tasks.data?.filter((t) => t.status === 'failed') ?? []
  const candidateMemories = memories.data?.filter((m) => m.status === 'candidate') ?? []

  if (agents.isLoading) return <PixelSpinner className="p-8" />

  return (
    <div>
      <h2 className="mb-6">SYSTEM OVERVIEW</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <PixelCard>
          <div className="text-center">
            <div className="text-3xl font-[var(--font-heading)] text-[var(--color-primary)]">
              {agents.data?.length ?? 0}
            </div>
            <div className="text-xs text-[var(--color-text-dim)] mt-1">Active Agents</div>
          </div>
        </PixelCard>

        <PixelCard>
          <div className="text-center">
            <div className="text-3xl font-[var(--font-heading)] text-[var(--color-accent)]">
              {runningTasks.length}
            </div>
            <div className="text-xs text-[var(--color-text-dim)] mt-1">Running Tasks</div>
          </div>
        </PixelCard>

        <PixelCard>
          <div className="text-center">
            <div className="text-3xl font-[var(--font-heading)] text-[var(--color-warning)]">
              {pendingApprovals.length}
            </div>
            <div className="text-xs text-[var(--color-text-dim)] mt-1">Pending Approvals</div>
          </div>
        </PixelCard>

        <PixelCard>
          <div className="text-center">
            <div className="text-3xl font-[var(--font-heading)] text-[var(--color-primary)]">
              {candidateMemories.length}
            </div>
            <div className="text-xs text-[var(--color-text-dim)] mt-1">New Memories</div>
          </div>
        </PixelCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PixelCard title="RUNNING TASKS">
          {runningTasks.length === 0 ? (
            <p className="text-sm text-[var(--color-text-dim)]">No running tasks</p>
          ) : (
            <div className="space-y-2">
              {runningTasks.slice(0, 5).map((t) => (
                <Link
                  key={t.task_id}
                  to="/tasks"
                  className="flex items-center justify-between p-2 border border-[var(--color-border)] hover:bg-[var(--color-panel)]"
                >
                  <div className="flex items-center gap-2">
                    <PixelStatusDot status={t.status} />
                    <span className="text-sm">{t.title}</span>
                  </div>
                  <PixelBadge label={t.priority} color={t.priority === 'high' ? 'red' : 'gray'} />
                </Link>
              ))}
            </div>
          )}
        </PixelCard>

        <PixelCard title="PENDING APPROVALS">
          {pendingApprovals.length === 0 ? (
            <p className="text-sm text-[var(--color-text-dim)]">No pending approvals</p>
          ) : (
            <div className="space-y-2">
              {pendingApprovals.slice(0, 5).map((a) => (
                <Link
                  key={a.approval_id}
                  to="/approvals"
                  className="flex items-center justify-between p-2 border border-[var(--color-border)] hover:bg-[var(--color-panel)]"
                >
                  <span className="text-sm">{a.summary}</span>
                  <PixelBadge
                    label={a.risk_level}
                    color={a.risk_level === 'high' ? 'red' : a.risk_level === 'medium' ? 'orange' : 'gray'}
                  />
                </Link>
              ))}
            </div>
          )}
        </PixelCard>

        <PixelCard title="FAILED TASKS">
          {failedTasks.length === 0 ? (
            <p className="text-sm text-[var(--color-text-dim)]">No failed tasks</p>
          ) : (
            <div className="space-y-2">
              {failedTasks.slice(0, 5).map((t) => (
                <div
                  key={t.task_id}
                  className="flex items-center justify-between p-2 border border-[var(--color-danger)]"
                >
                  <div className="flex items-center gap-2">
                    <PixelStatusDot status="failed" />
                    <span className="text-sm">{t.title}</span>
                  </div>
                  <span className="text-[10px] text-[var(--color-danger)]">
                    retries: {t.retry_count}
                  </span>
                </div>
              ))}
            </div>
          )}
        </PixelCard>

        <PixelCard title="RECENT MEMORIES">
          {memories.data?.length === 0 ? (
            <p className="text-sm text-[var(--color-text-dim)]">No memories yet</p>
          ) : (
            <div className="space-y-2">
              {(memories.data ?? []).slice(0, 5).map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between p-2 border border-[var(--color-border)]"
                >
                  <div className="flex items-center gap-2">
                    <PixelStatusDot status={m.status} />
                    <span className="text-sm truncate max-w-[300px]">{m.title}</span>
                  </div>
                  <PixelBadge label={m.type} color="blue" />
                </div>
              ))}
            </div>
          )}
        </PixelCard>
      </div>
    </div>
  )
}
