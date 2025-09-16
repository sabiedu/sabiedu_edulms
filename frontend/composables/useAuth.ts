import { useRuntimeConfig } from 'nuxt/app'

interface User {
  id: string
  username: string
  email: string
  firstName?: string
  lastName?: string
  role: string
  createdAt: string
}

interface AuthResponse {
  jwt: string
  user: User
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Initialize auth state from localStorage
  const initAuth = () => {
    if (process.client) {
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('auth_user')
      
      if (storedToken && storedUser) {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
      }
    }
  }

  const login = async (identifier: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${apiBase}/auth/local`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      })
      
      const data = await response.json()
      
      if (data.jwt && data.user) {
        token.value = data.jwt
        user.value = data.user
        
        // Store in localStorage
        if (process.client) {
          localStorage.setItem('auth_token', data.jwt)
          localStorage.setItem('auth_user', JSON.stringify(data.user))
        }
        
        return { success: true, user: data.user }
      } else {
        throw new Error(data.error?.message || 'Login failed')
      }
    } catch (err: any) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    firstName?: string
    lastName?: string
  }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${apiBase}/auth/local/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })
      
      const data = await response.json()
      
      if (data.jwt && data.user) {
        token.value = data.jwt
        user.value = data.user
        
        // Store in localStorage
        if (process.client) {
          localStorage.setItem('auth_token', data.jwt)
          localStorage.setItem('auth_user', JSON.stringify(data.user))
        }
        
        return { success: true, user: data.user }
      } else {
        throw new Error(data.error?.message || 'Registration failed')
      }
    } catch (err: any) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    
    if (process.client) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    }
  }

  const getAuthHeaders = () => {
    return token.value ? { Authorization: `Bearer ${token.value}` } : {}
  }

  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isInstructor = computed(() => user.value?.role === 'instructor' || user.value?.role === 'admin')

  // Initialize on composable creation
  initAuth()

  return {
    // State
    user: readonly(user),
    token: readonly(token),
    loading: readonly(loading),
    error: readonly(error),
    isAuthenticated,
    isAdmin,
    isInstructor,
    
    // Actions
    login,
    register,
    logout,
    getAuthHeaders,
    initAuth
  }
}
