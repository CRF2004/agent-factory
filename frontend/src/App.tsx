import { Routes, Route } from 'react-router-dom'
import { PixelLayout } from './components/ui/organisms/PixelLayout'
import Dashboard from './pages/Dashboard'
import AgentWorkspace from './pages/AgentWorkspace'
import AgentDesigner from './pages/AgentDesigner'
import AgentDetail from './pages/AgentDetail'
import TaskWorkspace from './pages/TaskWorkspace'
import MemoryWorkspace from './pages/MemoryWorkspace'
import ApprovalCenter from './pages/ApprovalCenter'

export default function App() {
  return (
    <PixelLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentWorkspace />} />
        <Route path="/agents/new" element={<AgentDesigner />} />
        <Route path="/agents/:id" element={<AgentDetail />} />
        <Route path="/tasks" element={<TaskWorkspace />} />
        <Route path="/memory" element={<MemoryWorkspace />} />
        <Route path="/approvals" element={<ApprovalCenter />} />
      </Routes>
    </PixelLayout>
  )
}
