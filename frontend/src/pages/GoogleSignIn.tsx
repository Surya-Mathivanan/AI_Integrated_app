import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

export default function GoogleSignIn() {
  const navigate = useNavigate()
  const { isAuthenticated, signInWithGoogle } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true })
  }, [isAuthenticated, navigate])

  return (
    <div className="card">
      <h2>Continue with Google</h2>
      <p className="muted">Sign in to create and track your personalized preparation plan.</p>
      <button className="btn" onClick={() => signInWithGoogle()}>Continue with Google</button>
    </div>
  )
}