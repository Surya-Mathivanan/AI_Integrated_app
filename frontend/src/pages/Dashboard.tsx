import { useEffect, useMemo, useState } from 'react'
import api from '../api/client'
import { Link } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'

interface PathwayMeta { id: string; title: string; days: number; createdAt?: string }

export default function Dashboard() {
  const [pathway, setPathway] = useState<any | null>(null)
  const [tips, setTips] = useState<string[]>([])
  const [list, setList] = useState<PathwayMeta[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
      const [{ data: p }, { data: m }, { data: l }] = await Promise.all([
        api.get('/api/pathway/current'),
        api.get('/api/motivation'),
        api.get('/api/pathway/list'),
      ])
      setPathway(p.pathway)
      setTips(m.tips || [])
      setList(l.items || [])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const totalItems = useMemo(() => {
    const s = pathway?.sections || {}
    const all = [ ...(s.codingProblems||[]), ...(s.youtubeReferences||[]), ...(s.theoryContent||[]) ]
    return all.length
  }, [pathway])

  const doneItems = useMemo(() => {
    const s = pathway?.sections || {}
    const all = [ ...(s.codingProblems||[]), ...(s.youtubeReferences||[]), ...(s.theoryContent||[]) ]
    return all.filter((i:any)=>i.completed).length
  }, [pathway])

  const progress = totalItems ? Math.round((doneItems / totalItems) * 100) : 0

  if (loading) {
    return (
      <div className="grid-2">
        <div className="card">
          <div className="page-loading">
            <div className="page-loading-spinner"></div>
            <p className="muted">Loading your dashboard...</p>
          </div>
        </div>
        <div className="card">
          <div className="skeleton" style={{ height: '200px' }}></div>
        </div>
      </div>
    )
  }

  return (
    <div className="grid-2">
      <div className="card">
        <div className="row" style={{justifyContent:'space-between'}}>
          <h2>Overview</h2>
          <Link to="/questionnaire" className="btn">Create New Pathway</Link>
        </div>
        {pathway ? (
          <>
            <p className="muted">{pathway.title}</p>
            <ProgressBar value={progress} />
            <div className="metrics">
              <div className="metric"><div className="metric-value">{totalItems}</div><div className="metric-label">Total Items</div></div>
             
              <div className="metric"><div className="metric-value">{pathway.schedule?.daily?.length||0}</div><div className="metric-label">Days</div></div>
            </div>
            <div className="row">
              <Link to="/pathway" className="btn">Open Pathway</Link>
              <Link to="/chat" className="btn secondary">Ask AI</Link>
              <Link to="/pathway" className="btn">Generate PDF</Link>
            </div>
          </>
        ) : (
          <>
            <p>No pathway yet.</p>
            <Link to="/questionnaire" className="btn">Create Your Pathway</Link>
          </>
        )}
      </div>
      <div className="card">
        <h2>Your Pathways ({list.length})</h2>
        {list.length === 0 ? (
          <p className="muted">No pathways yet.</p>
        ) : (
          <ul className="list">
            {list.map(p => (
              <li key={p.id} className="list-item">
                <div>
                  <div><b>{p.title}</b></div>
                  <div className="muted" style={{fontSize:12}}>Days: {p.days}{p.createdAt ? ` • Created: ${new Date(p.createdAt).toLocaleString()}` : ''}</div>
                </div>
                <Link to="/pathway" className="btn small">Open</Link>
              </li>
            ))}
          </ul>
        )}
        <h3 style={{marginTop:16}}>Motivational Tips</h3>
        <ul>
          {tips.map((tip, i) => <li key={i}>• {tip}</li>)}
        </ul>
      </div>
    </div>
  )
}