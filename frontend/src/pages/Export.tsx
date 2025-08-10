import { useEffect, useRef, useState } from 'react'
import api from '../api/client'

export default function ExportPage() {
  const [pathway, setPathway] = useState<any | null>(null)
  const [exporting, setExporting] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api.get('/api/pathway/current').then(({ data }) => setPathway(data.pathway)).catch(console.error)
  }, [])

  const exportPDF = async () => {
    if (!ref.current) return
    setExporting(true)
    try {
      const content = ref.current
      const blob = new Blob([content.innerText], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'plan.txt' // simple fallback; can integrate jsPDF later
      a.click()
      URL.revokeObjectURL(url)
      alert('Exported (as .txt placeholder). You can integrate jsPDF for PDF rendering.')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="card">
      <h2>Export Plan</h2>
      <div ref={ref} className="pre">
        {pathway ? JSON.stringify(pathway, null, 2) : 'Loading...'}
      </div>
      <button className="btn" onClick={exportPDF} disabled={exporting}>{exporting ? 'Exporting...' : 'Export as PDF'}</button>
    </div>
  )
}