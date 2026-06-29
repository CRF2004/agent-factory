const BASE = '/api'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail.detail || res.statusText)
  }
  return res.json()
}

export interface AgentSpec {
  agent_id: string
  name: string
  role: string
  mission: string
  status: string
  autonomy_level: string
  project_ids: string[]
  triggers: Record<string, unknown>[]
  tools: Record<string, unknown>[]
  memory_access: Record<string, unknown>
  actions: Record<string, unknown>
  evaluation: string[]
  created_at?: string
  updated_at?: string
}

export interface TaskSpec {
  task_id: string
  title: string
  type: string
  owner_agent: string
  project_id?: string
  status: string
  priority: string
  created_by: string
  input: Record<string, unknown>
  expected_output: string[]
  output: Record<string, unknown>
  requires_approval: boolean
  dependencies: string[]
  next_action?: string
  retry_count: number
  created_at?: string
  updated_at?: string
}

export interface AgentRun {
  id: string
  agent_id: string
  task_id: string
  status: string
  input: Record<string, unknown>
  output: Record<string, unknown>
  started_at: string
  ended_at?: string
  error_message?: string
  cost?: number
}

export interface ToolCall {
  id: string
  run_id: string
  tool_id: string
  input: Record<string, unknown>
  output: Record<string, unknown>
  status: string
  risk_level: string
}

export interface MemoryItem {
  id: string
  type: string
  title: string
  content: string
  summary: string
  source?: string
  source_task_id?: string
  source_run_id?: string
  status: string
  confidence: number
  reliability_score?: number
  tags: string[]
  related_projects: string[]
  created_by_agent_id?: string
  created_at?: string
}

export interface ApprovalRequest {
  approval_id: string
  requesting_agent: string
  task_id?: string
  action_type: string
  risk_level: string
  summary: string
  details: Record<string, unknown>
  status: string
  user_decision?: string
  decided_at?: string
  created_at?: string
}

export interface ToolSpec {
  tool_id: string
  name: string
  type: string
  description: string
  permission: string
  risk_level: string
  requires_approval: boolean
  allowed_agents: string[]
  config_schema: Record<string, unknown>
  enabled: boolean
}

// agents
export const createAgent = (agent: AgentSpec) =>
  request<AgentSpec>('/agents', { method: 'POST', body: JSON.stringify(agent) })

export const listAgents = () => request<AgentSpec[]>('/agents')

export const getAgent = (id: string) => request<AgentSpec>(`/agents/${id}`)

// tasks
export const createTask = (task: TaskSpec) =>
  request<TaskSpec>('/tasks', { method: 'POST', body: JSON.stringify(task) })

export const listTasks = () => request<TaskSpec[]>('/tasks')

export const getTask = (id: string) => request<TaskSpec>(`/tasks/${id}`)

export const runTask = (id: string) =>
  request<AgentRun>(`/tasks/${id}/run`, { method: 'POST' })

// runs
export const listRuns = () => request<AgentRun[]>('/runs')

// tool calls
export const listToolCalls = () => request<ToolCall[]>('/tool-calls')

// memory
export const listMemoryItems = () => request<MemoryItem[]>('/memory-items')

// approvals
export const listApprovals = () => request<ApprovalRequest[]>('/approvals')

export const approveAction = (id: string) =>
  request<ApprovalRequest>(`/approvals/${id}/approve`, { method: 'POST' })

export const rejectAction = (id: string) =>
  request<ApprovalRequest>(`/approvals/${id}/reject`, { method: 'POST' })

// tools
export const registerTool = (tool: ToolSpec) =>
  request<ToolSpec>('/tools', { method: 'POST', body: JSON.stringify(tool) })

export const listTools = () => request<ToolSpec[]>('/tools')

export const getTool = (id: string) => request<ToolSpec>(`/tools/${id}`)
