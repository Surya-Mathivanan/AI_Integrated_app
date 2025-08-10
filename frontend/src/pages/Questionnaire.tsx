import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

 type Level = 'beginner' | 'intermediate' | 'advanced'

export default function Questionnaire() {
  const navigate = useNavigate()

  const [step, setStep] = useState<'landing'|'level'|'details'|'quiz'|'confirm'>('landing')
  const [level, setLevel] = useState<Level>('beginner')
  const [hoursPerDay, setHoursPerDay] = useState<'1-2'|'2-3'|'3-4'|'>4'>('1-2')
  const [language, setLanguage] = useState<'python'|'java'|'cpp'|'javascript'|'c'>('python')
  const [duration, setDuration] = useState<'1 week'|'1 month'|'3 months'>('1 week')
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const needQuiz = level !== 'beginner'

  const startNew = async () => {
    setError(null)
    // Move to level immediately for better UX
    setStep('level')
    setLoading(true)
    try {
      await api.post('/api/pathway/new')
    } catch (e:any) {
      const status = e?.response?.status
      if (status === 401) {
        // Not signed in – redirect to signin
        navigate('/signin', { replace: true })
        return
      }
      // Keep wizard open even if backend reset failed; show a non-blocking message
      setError(e?.response?.data?.error || 'Could not initialize a new pathway, you can still continue.')
    } finally {
      setLoading(false)
    }
  }

  const onStart = () => { void startNew() }
  const selectLevel = (l: Level) => { setLevel(l); setStep('details') }

  const submitDetails = () => {
    if (needQuiz) setStep('quiz')
    else setStep('confirm')
  }

  const finishQuiz = (score: number) => {
    setQuizScore(score)
    if (level === 'intermediate' && score < 8) setLevel('beginner')
    if (level === 'advanced' && score < 8) setLevel('intermediate')
    setStep('confirm')
  }

  const onGenerate = async () => {
    setError(null)
    setLoading(true)
    try {
      const payload = {
        skillLevel: level,
        hoursPerDay,
        programmingLanguage: language,
        prepTime: duration,
      }
      await api.post('/api/pathway/generate', payload)
      navigate('/pathway')
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Failed to generate pathway')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wizard">
      {step === 'landing' && (
        <section className="hero">
          <h1>Your Personalized DSA Pathway</h1>
          <p className="muted">Answer a few questions and get a complete plan: schedule plus curated coding, video, and theory content.</p>
          <button className="btn" onClick={onStart} disabled={loading}>{loading? 'Starting...' : 'Start'}</button>
          {error && <div className="error" style={{marginTop:8}}>{error}</div>}
        </section>
      )}

      {step === 'level' && (
        <section className="card">
          <h2>Select Your Level</h2>
          <div className="row wrap">
            {(['beginner','intermediate','advanced'] as Level[]).map(l => (
              <button key={l} className={`pill ${l===level?'active':''}`} onClick={() => selectLevel(l)}>
                {l[0].toUpperCase()+l.slice(1)}
              </button>
            ))}
          </div>
          {error && <div className="error" style={{marginTop:8}}>{error}</div>}
        </section>
      )}

      {step === 'details' && (
        <section className="card">
          <h2>Study Details</h2>
          <div className="grid">
            <label>Hours per day
              <select value={hoursPerDay} onChange={(e)=>setHoursPerDay(e.target.value as any)}>
                <option value="1-2">1–2 hours</option>
                <option value="2-3">2–3 hours</option>
                <option value="3-4">3–4 hours</option>
                <option value=">4">More than 4 hours</option>
              </select>
            </label>
            <label>Preferred Language
              <select value={language} onChange={(e)=>setLanguage(e.target.value as any)}>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="javascript">JavaScript</option>
                <option value="c">C</option>
              </select>
            </label>
            <label>Duration
              <select value={duration} onChange={(e)=>setDuration(e.target.value as any)}>
                <option value="1 week">1 week</option>
                <option value="1 month">1 month</option>
                <option value="3 months">3 months</option>
              </select>
            </label>
          </div>
          <div className="row">
            <button className="btn" onClick={submitDetails}>Continue</button>
          </div>
        </section>
      )}

      {step === 'quiz' && (
        <section className="card">
          <h2>{level[0].toUpperCase()+level.slice(1)} Level Quiz</h2>
          <p className="muted">Answer 10 questions. For demo, click a score:</p>
          <div className="row wrap">
            {[...Array(11)].map((_,i)=> (
              <button key={i} className="pill" onClick={()=>finishQuiz(i)}>{i}/10</button>
            ))}
          </div>
        </section>
      )}

      {step === 'confirm' && (
        <section className="card">
          <h2>Confirm & Generate</h2>
          <ul className="list">
            <li>Level: <b>{level}</b></li>
            <li>Hours/day: <b>{hoursPerDay}</b></li>
            <li>Language: <b>{language}</b></li>
            <li>Duration: <b>{duration}</b></li>
            {quizScore !== null && <li>Quiz score: <b>{quizScore}/10</b></li>}
          </ul>
          {error && <div className="error">{error}</div>}
          <div className="row">
            <button className="btn" onClick={onGenerate} disabled={loading}>{loading? 'Generating...' : 'Generate Pathway'}</button>
          </div>
        </section>
      )}
    </div>
  )
}