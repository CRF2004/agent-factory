import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listApprovals, approveAction, rejectAction, type ApprovalRequest } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelBadge } from '../components/ui/atoms/PixelBadge'
import { PixelButton } from '../components/ui/atoms/PixelButton'
import { PixelSpinner } from '../components/ui/atoms/PixelSpinner'

const riskColors: Record<string, 'green' | 'orange' | 'red'> = {
  low: 'green',
  medium: 'orange',
  high: 'red',
  critical: 'red',
}

const statusColors: Record<string, 'orange' | 'green' | 'red' | 'gray'> = {
  pending: 'orange',
  approved: 'green',
  rejected: 'red',
  needs_revision: 'orange',
  expired: 'gray',
}

export default function ApprovalCenter() {
  const queryClient = useQueryClient()
  const approvals = useQuery({ queryKey: ['approvals'], queryFn: listApprovals, refetchInterval: 10000 })

  const approve = useMutation({
    mutationFn: approveAction,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approvals'] }),
  })

  const reject = useMutation({
    mutationFn: rejectAction,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approvals'] }),
  })

  if (approvals.isLoading) return <PixelSpinner className="p-8" />

  const data = approvals.data ?? []
  const pending = data.filter((a) => a.status === 'pending')
  const history = data.filter((a) => a.status !== 'pending')

  return (
    <div>
      <h2 className="mb-6">APPROVAL CENTER</h2>

      <h3 className="text-[var(--color-warning)] mb-4">PENDING ({pending.length})</h3>

      <div className="space-y-3 mb-8">
        {pending.map((a: ApprovalRequest) => (
          <PixelCard key={a.approval_id}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-[var(--color-warning)] m-0">{a.action_type}</h4>
                <p className="text-sm text-[var(--color-text)] mt-1">{a.summary}</p>
                <div className="flex gap-2 mt-2">
                  <PixelBadge label={a.risk_level} color={riskColors[a.risk_level] ?? 'gray'} />
                  <PixelBadge label={`by ${a.requesting_agent}`} color="gray" />
                  {a.task_id && <PixelBadge label={`task: ${a.task_id}`} color="blue" />}
                </div>
                {Object.keys(a.details).length > 0 && (
                  <pre className="text-[10px] text-[var(--color-text-dim)] mt-2 font-[var(--font-mono)]">
                    {JSON.stringify(a.details, null, 2)}
                  </pre>
                )}
              </div>
              <div className="flex gap-2 flex-shrink-0 ml-4">
                <PixelButton
                  size="sm"
                  variant="primary"
                  onClick={() => approve.mutate(a.approval_id)}
                  disabled={approve.isPending}
                >
                  APPROVE
                </PixelButton>
                <PixelButton
                  size="sm"
                  variant="danger"
                  onClick={() => reject.mutate(a.approval_id)}
                  disabled={reject.isPending}
                >
                  REJECT
                </PixelButton>
              </div>
            </div>
          </PixelCard>
        ))}

        {pending.length === 0 && (
          <p className="text-sm text-[var(--color-text-dim)] text-center py-8">
            No pending approvals — all clear.
          </p>
        )}
      </div>

      {history.length > 0 && (
        <>
          <h3 className="text-[var(--color-text-dim)] mb-4">HISTORY</h3>
          <div className="space-y-1">
            {history.slice(0, 20).map((a) => (
              <div
                key={a.approval_id}
                className="flex items-center justify-between p-2 border border-[var(--color-border)]"
              >
                <div className="flex items-center gap-2">
                  <PixelBadge label={a.status} color={statusColors[a.status] ?? 'gray'} />
                  <span className="text-sm">{a.summary}</span>
                </div>
                <div className="flex gap-2">
                  <PixelBadge label={a.risk_level} color={riskColors[a.risk_level] ?? 'gray'} />
                  <span className="text-[10px] text-[var(--color-text-dim)]">
                    {a.requesting_agent}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
