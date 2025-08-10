import { useEffect, useRef, useState } from 'react'
import api from '../api/client'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { Link } from 'react-router-dom'

interface SectionItem { id: string; title: string; url?: string; completed?: boolean }

export default function Pathway() {
  const [pathway, setPathway] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/api/pathway/current')
      setPathway(data.pathway)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load().catch(console.error) }, [])

  const toggleItem = async (item: SectionItem) => {
    try {
      await api.patch('/api/pathway/progress', { itemId: item.id })
      await load()
    } catch (e) {
      console.error(e)
    }
  }

  const exportPDF = async () => {
    if (!ref.current) return
    setExporting(true)
    try {
      const canvas = await html2canvas(ref.current, { scale: 2 })
      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()

      const imgWidth = pageWidth
      const imgHeight = (canvas.height * pageWidth) / canvas.width
      let heightLeft = imgHeight
      let position = 0

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight

      while (heightLeft > 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
      }

      pdf.save('DSA-Plan.pdf')
    } finally {
      setExporting(false)
    }
  }

  if (loading) return <div className="card"><p>Loading...</p></div>
  if (!pathway) return (
    <div className="card">
      <p>No pathway found.</p>
      <Link className="btn" to="/questionnaire">Create New Pathway</Link>
    </div>
  )

  const sections = pathway.sections || {}
  const coding: SectionItem[] = sections.codingProblems || []
  const youtube: SectionItem[] = sections.youtubeReferences || []
  const theory: SectionItem[] = sections.theoryContent || []

  return (
    <div className="layout-2">
      <div className="card" ref={ref}>
        <h2>{pathway.title || 'DSA Pathway'}</h2>

        <h3>Daily Schedule</h3>
        <p className="muted">Tip: Ask the AI for more examples or a deeper breakdown for any day.</p>
        <div className="schedule-grid">
          {pathway.schedule?.daily?.map((d: any) => (
            <div key={d.day} className="schedule-card">
              <div className="schedule-day">Day {d.day}</div>
              <div className="schedule-focus">{d.focus}</div>
              <div className="schedule-time">{d.time} hrs</div>
              {Array.isArray(d.topics) && d.topics.length > 0 && (
                <ul className="mini-list">
                  {d.topics.map((t: string, i: number) => <li key={i}>• {t}</li>)}
                </ul>
              )}
              {d.details && <div className="muted" style={{marginTop:8}}>{d.details}</div>}

              {d.resources && (
                <div className="day-links" style={{marginTop:10}}>
                  <div className="day-group">
                    <div className="small-title">Practice</div>
                    <ul className="mini-list">
                      {d.resources.practice?.map((r: any) => (
                        <li key={r.id}><a href={r.url} target="_blank">{r.title}</a></li>
                      ))}
                    </ul>
                  </div>
                  <div className="day-group">
                    <div className="small-title">YouTube</div>
                    <ul className="mini-list">
                      {d.resources.youtube?.map((r: any) => (
                        <li key={r.id}><a href={r.url} target="_blank">{r.title}</a></li>
                      ))}
                    </ul>
                  </div>
                  <div className="day-group">
                    <div className="small-title">Theory</div>
                    <ul className="mini-list">
                      {d.resources.theory?.map((r: any) => (
                        <li key={r.id}><a href={r.url} target="_blank">{r.title}</a></li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="sections">
        </div>
      </div>

      <div className="card sidebar">
        <h3>Actions</h3>
        {/* <Link className="btn secondary" to="/questionnaire">Create New Pathway</Link> */}
        <button className="btn" onClick={exportPDF} disabled={exporting}>{exporting? 'Generating...' : 'Generate PDF'}</button>
      </div>
    </div>
  )
}