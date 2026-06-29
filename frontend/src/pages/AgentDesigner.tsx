import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createAgent, type AgentSpec } from '../lib/api'
import { PixelCard } from '../components/ui/molecules/PixelCard'
import { PixelButton } from '../components/ui/atoms/PixelButton'

const DEFAULT_AGENT: AgentSpec = {
  agent_id: '',
  name: '',
  role: 'Research Agent',
  mission: '',
  status: 'idle',
  autonomy_level: 'L2',
  project_ids: [],
  triggers: [],
  tools: [
    { tool_id: 'web_search', permission: 'read_only' },
    { tool_id: 'llm_call', permission: 'read_only' },
  ],
  memory_access: {
    read: ['knowledge_base'],
    write: ['candidate_memory'],
    require_source: true,
    low_confidence_requires_review: true,
  },
  actions: {
    auto: ['search_sources', 'summarize', 'score_relevance', 'create_candidate_memory'],
    approval_required: ['write_long_term_memory'],
  },
  evaluation: ['source_required', 'relevance_score_required'],
}

const ROLES = ['Research Agent', 'Project Manager Agent', 'Memory Curator Agent']
const AUTONOMY_LEVELS = ['L0', 'L1', 'L2', 'L3']

export default function AgentDesigner() {
  const navigate = useNavigate()
  const [form, setForm] = useState<AgentSpec>(DEFAULT_AGENT)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!form.name.trim() || !form.agent_id.trim()) {
      setError('Agent ID and Name are required')
      return
    }
    setSaving(true)
    setError('')
    try {
      await createAgent(form)
      navigate('/agents')
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  const inputClass =
    'w-full px-3 py-2 text-sm font-[var(--font-body)] bg-[var(--color-panel)] border-2 border-[var(--color-border)] text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none'

  return (
    <div className="max-w-2xl">
      <h2 className="mb-6">AGENT DESIGNER</h2>

      <PixelCard title="BASIC INFO" className="mb-4">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-[var(--font-heading)] text-[var(--color-text-dim)] block mb-1">
              AGENT ID
            </label>
            <input
              className={inputClass}
              value={form.agent_id}
              onChange={(e) => setForm({ ...form, agent_id: e.target.value })}
              placeholder="research_agent_ecg"
            />
          </div>
          <div>
            <label className="text-xs font-[var(--font-heading)] text-[var(--color-text-dim)] block mb-1">
              NAME
            </label>
            <input
              className={inputClass}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="ECG Research Agent"
            />
          </div>
          <div>
            <label className="text-xs font-[var(--font-heading)] text-[var(--color-text-dim)] block mb-1">
              ROLE
            </label>
            <select
              className={inputClass}
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-[var(--font-heading)] text-[var(--color-text-dim)] block mb-1">
              AUTONOMY LEVEL
            </label>
            <select
              className={inputClass}
              value={form.autonomy_level}
              onChange={(e) => setForm({ ...form, autonomy_level: e.target.value })}
            >
              {AUTONOMY_LEVELS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-[var(--font-heading)] text-[var(--color-text-dim)] block mb-1">
              MISSION
            </label>
            <textarea
              className={inputClass}
              rows={3}
              value={form.mission}
              onChange={(e) => setForm({ ...form, mission: e.target.value })}
              placeholder="Monitor ECG and medical AI research..."
            />
          </div>
        </div>
      </PixelCard>

      <PixelCard title="AGENT SPEC PREVIEW" className="mb-4">
        <pre className="text-xs text-[var(--color-text-dim)] overflow-auto max-h-64 font-[var(--font-mono)]">
          {JSON.stringify(form, null, 2)}
        </pre>
      </PixelCard>

      {error && (
        <div className="p-3 mb-4 border-2 border-[var(--color-danger)] text-[var(--color-danger)] text-sm">
          ERROR: {error}
        </div>
      )}

      <div className="flex gap-3">
        <PixelButton onClick={handleSave} disabled={saving}>
          {saving ? 'SAVING...' : 'SAVE AGENT'}
        </PixelButton>
        <PixelButton variant="ghost" onClick={() => navigate('/agents')}>
          CANCEL
        </PixelButton>
      </div>
    </div>
  )
}
