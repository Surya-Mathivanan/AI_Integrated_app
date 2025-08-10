import { create } from 'zustand'
import { User } from 'firebase/auth'
import { subscribeAuth, signInWithGoogle as firebaseSignIn, logoutFirebase } from '../firebase'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  signInWithGoogle: () => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => {
  // subscribe to firebase
  subscribeAuth((user) => set({ user, isAuthenticated: !!user }))

  return {
    user: null,
    isAuthenticated: false,
    async signInWithGoogle() {
      await firebaseSignIn()
    },
    async logout() {
      await logoutFirebase()
    },
  }
})