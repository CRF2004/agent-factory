import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listTasks, runTask, type TaskSpec } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelStatusDot } from '../components/ui/molecules/PixelStatusDot'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelButton } from '../components/ui/atoms/PixelButton'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'
import { useState } from 'react'

const statusColumns = ['created', 'queued', 'running', 'waiting_approval', 'completed', 'failed']

const statusColors: Record<string, 'green' | 'orange' | 'red' | 'blue' | 'gray'> = {
  created: 'gray',
  queued: 'blue',
  running: 'blue',
  waiting_approval: 'orange',
  completed: 'green',
  failed: 'red',
  cancelled: 'red',
  blocked: 'orange',
}

export default function TaskWorkspace() {
  const queryClient = useQueryClient()
  const tasks = useQuery({ queryKey: ['tasks'], queryFn: listTasks, refetchInterval: 5000 })
  const [expandedTask, setExpandedTask] = useState<string | null>(null)

  const runMutation = useMutation({
    mutationFn: runTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['runs'] })
      queryClient.invalidateQueries({ queryKey: ['memories'] })
    },
  })

  if (tasks.isLoading) return <PixelSpinner className="p-8" />

  const taskList = tasks.data ?? []

  return (
    <div>
      <h2 className="mb-6">TASK WORKSPACE</h2>

      <div className="grid grid-cols-1 xl:grid-cols-6 gap-4 mb-6">
        {statusColumns.map((status) => {
          const items = taskList.filter((t) => t.status === status)
          return (
            <PixelCard key={status} title={status.toUpperCase()} className="min-h-[120px]">
              <div className="text-xs text-[var(--color-text-dim)] mb-2">{items.length} tasks</div>
              <div className="space-y-1">
                {items.slice(0, 5).map((t) => (
                  <button
                    key={t.task_id}
                    className="w-full text-left p-2 border border-[var(--color-border)] hover:bg-[var(--color-panel)] text-xs"
                    onClick={() => setExpandedTask(expandedTask === t.task_id ? null : t.task_id)}
                  >
                    <div className="flex items-center gap-1 mb-1">
                      <PixelStatusDot status={t.status} />
                      <span className="truncate">{t.title}</span>
                    </div>
                    <div className="flex gap-1">
                      <PixelBadge label={t.priority} color={t.priority === 'high' || t.priority === 'critical' ? 'red' : 'gray'} />
                      <PixelBadge label={t.type} color="blue" />
                    </div>
                  </button>
                ))}
              </div>
            </PixelCard>
          )
        })}
      </div>

      <PixelCard title="ALL TASKS">
        <div className="space-y-1">
          {taskList.map((t: TaskSpec) => (
            <div key={t.task_id}>
              <div className="flex items-center justify-between p-2 border border-[var(--color-border)] hover:bg-[var(--color-panel)]">
                <button
                  className="flex items-center gap-2 flex-1 text-left"
                  onClick={() => setExpandedTask(expandedTask === t.task_id ? null : t.task_id)}
                >
                  <PixelStatusDot status={t.status} />
                  <span className="text-sm">{t.title}</span>
                  <PixelBadge label={t.type} color="blue" />
                </button>
                <div className="flex items-center gap-2">
                  <PixelBadge label={t.status} color={statusColors[t.status] ?? 'gray'} />
                  {(t.status === 'created' || t.status === 'queued' || t.status === 'failed') && (
                    <PixelButton
                      size="sm"
                      variant="primary"
                      onClick={() => runMutation.mutate(t.task_id)}
                      disabled={runMutation.isPending}
                    >
                      RUN
                    </PixelButton>
                  )}
                </div>
              </div>

              {expandedTask === t.task_id && (
                <div className="p-3 border-x border-b border-[var(--color-border)] bg-[var(--color-panel)] text-xs space-y-1">
                  <div>
                    <span className="text-[var(--color-text-dim)]">ID: </span>
                    {t.task_id}
                  </div>
                  <div>
                    <span className="text-[var(--color-text-dim)]">Agent: </span>
                    {t.owner_agent}
                  </div>
                  <div>
                    <span className="text-[var(--color-text-dim)]">Input: </span>
                    <pre className="inline text-[10px] font-[var(--font-mono)]">
                      {JSON.stringify(t.input, null, 2)}
                    </pre>
                  </div>
                  {Object.keys(t.output).length > 0 && (
                    <div>
                      <span className="text-[var(--color-text-dim)]">Output: </span>
                      <pre className="inline text-[10px] font-[var(--font-mono)] text-[var(--color-primary)]">
                        {JSON.stringify(t.output, null, 2)}
                      </pre>
                    </div>
                  )}
                  {t.retry_count > 0 && (
                    <div>
                      <span className="text-[var(--color-text-dim)]">Retries: </span>
                      <span className="text-[var(--color-warning)]">{t.retry_count}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {taskList.length === 0 && (
            <p className="text-sm text-[var(--color-text-dim)] text-center py-8">
              No tasks yet. Create a task via the API.
            </p>
          )}
        </div>
      </PixelCard>
    </div>
  )
}
