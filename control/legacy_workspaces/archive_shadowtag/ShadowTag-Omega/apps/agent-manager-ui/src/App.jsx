import { useState, useEffect } from 'react'
import { A2UIRenderer } from './components/A2UIRenderer'

function App() {
  const [state, setState] = useState({ agents: [], tasks: [] })
  const [taskInput, setTaskInput] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchState = async () => {
    try {
      const res = await fetch('/ui/state')
      if (res.ok) {
        const data = await res.json()
        setState(data)
      }
    } catch (e) {
      console.error("Failed to fetch state", e)
    }
  }

  // Poll for updates every 2 seconds
  useEffect(() => {
    fetchState()
    const interval = setInterval(fetchState, 2000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!taskInput.trim()) return

    setLoading(true)
    try {
      await fetch('/ui/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: taskInput })
      })
      setTaskInput('')
      fetchState()
    } catch (e) {
      console.error("Failed to submit task", e)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (action, data) => {
     console.log("Action triggered:", action, data);
     // Future: Send action back to backend
  }

  return (
    <div className="container">
      <header>
        <h1>Agent Manager // Autoresearch</h1>
        <div style={{fontSize: '0.8rem', color: '#8b949e', marginTop: '0.5rem'}}>
           F.L.O.W. Framework Active
        </div>
      </header>
      
      <div className="dashboard-grid">
        <main>
          <div className="card">
            <h2>Live Operations</h2>
            <div className="log-feed">
              {state.tasks.length === 0 && <div style={{color: '#666'}}>No recent activity. System ready.</div>}
              {state.tasks.slice().reverse().map((task) => ( // Reverse to show newest first
                <div key={task.id} style={{marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #30363d'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                      <div style={{color: '#58a6ff', fontWeight: 'bold'}}>➜ {task.task}</div>
                      <span style={{fontSize: '0.7rem', color: '#666'}}>
                        {new Date(task.timestamp).toLocaleTimeString()}
                      </span>
                  </div>
                  <div style={{marginLeft: '1rem', color: '#ccc'}}>
                     <A2UIRenderer payload={task.outcome} onAction={handleAction} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2>Command Center</h2>
            <form className="task-input-area" onSubmit={handleSubmit}>
              <input 
                type="text" 
                placeholder="Enter operational directive (e.g. 'Scan src/main.py')" 
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Dispatching...' : 'Dispatch'}
              </button>
            </form>
          </div>
        </main>

        <aside>
          <div className="card">
            <h2>Active Agents</h2>
            <div className="agent-list">
              {state.agents.map((agent) => (
                <div key={agent.name} className="agent-item">
                  <div>
                    <div style={{fontWeight: 'bold'}}>{agent.name}</div>
                    <div style={{fontSize: '0.8rem', color: '#8b949e'}}>{agent.role}</div>
                  </div>
                  <span className={`status-badge status-${agent.status.toLowerCase()}`}>
                    {agent.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default App
