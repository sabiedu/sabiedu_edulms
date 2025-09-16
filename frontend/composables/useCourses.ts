import { useRuntimeConfig } from 'nuxt/app'

interface Course {
  id: number
  title: string
  description: string
  instructor_id?: string
  category_id?: number
  difficulty: string
  duration: number
  quality_score?: number
  learning_objectives?: string[]
  prerequisites?: string[]
  created_at: string
  updated_at: string
}

interface Lesson {
  id: number
  course_id: number
  title: string
  content: string
  lesson_order: number
  duration: number
  lesson_type: string
  ai_metadata?: any
  created_at: string
  updated_at: string
}

interface UserProgress {
  id: number
  user_id: string
  course_id: number
  lesson_id: number
  progress_percentage: number
  completion_status: string
  time_spent: number
  last_accessed: string
}

export const useCourses = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const lessons = ref<Lesson[]>([])
  const userProgress = ref<UserProgress[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCourses = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${apiBase}/lms/courses`)
      const data = await response.json()
      
      if (data.success) {
        courses.value = data.data || []
      } else {
        throw new Error(data.error || 'Failed to fetch courses')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Error fetching courses:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchCourse = async (courseId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${apiBase}/lms/courses/${courseId}`)
      const data = await response.json()
      
      if (data.success) {
        currentCourse.value = data.data
      } else {
        throw new Error(data.error || 'Failed to fetch course')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Error fetching course:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchLessons = async (courseId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${apiBase}/lms/courses/${courseId}/lessons`)
      const data = await response.json()
      
      if (data.success) {
        lessons.value = data.data || []
      } else {
        throw new Error(data.error || 'Failed to fetch lessons')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Error fetching lessons:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchUserProgress = async (userId: string, courseId?: number) => {
    loading.value = true
    error.value = null
    
    try {
      const url = courseId 
        ? `${apiBase}/lms/users/${userId}/progress?courseId=${courseId}`
        : `${apiBase}/lms/users/${userId}/progress`
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (data.success) {
        userProgress.value = data.data || []
      } else {
        throw new Error(data.error || 'Failed to fetch user progress')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Error fetching user progress:', err)
    } finally {
      loading.value = false
    }
  }

  const updateProgress = async (userId: string, lessonId: number, progressData: {
    progress_percentage?: number
    completion_status?: string
    time_spent?: number
  }) => {
    try {
      const response = await fetch(`${apiBase}/lms/users/${userId}/progress`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          ...progressData
        })
      })
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to update progress')
      }
      
      return data.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error updating progress:', err)
      throw err
    }
  }

  return {
    // State
    courses: readonly(courses),
    currentCourse: readonly(currentCourse),
    lessons: readonly(lessons),
    userProgress: readonly(userProgress),
    loading: readonly(loading),
    error: readonly(error),
    
    // Actions
    fetchCourses,
    fetchCourse,
    fetchLessons,
    fetchUserProgress,
    updateProgress
  }
}
